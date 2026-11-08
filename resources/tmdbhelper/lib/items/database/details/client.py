import socket
from contextlib import contextmanager
from time import monotonic, perf_counter
from xbmc import Monitor
from tmdbhelper.lib.addon.consts import RUNSCRIPT
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.plugin import executebuiltin, get_version
from tmdbhelper.lib.files.sqlite_mutex import SQLiteMutex
from tmdbhelper.lib.items.database.details.protocol import (
    DetailsServiceError, DetailsServiceUnavailable, MAX_REQUEST_ITEMS,
    PING_TIMEOUT, PROTOCOL_VERSION, REQUEST_TIMEOUT, ServiceLocation,
    receive_message, send_message,
)


class DetailsClient:
    def __init__(self):
        self.monitor = Monitor()
        self.location = ServiceLocation()
        self.version = get_version()
        self.timings = {}  # Stage seconds summed over batches when the service reports timings

    def exchange(self, endpoint, items=None, kodi_details=False, prepare=None, invalidate=False):
        with socket.create_connection(('127.0.0.1', endpoint['port']), timeout=2) as connection:
            connection.settimeout(5)
            send_message(connection, {
                'version': PROTOCOL_VERSION, 'token': endpoint['token'],
                'items': items, 'kodi_details': kodi_details, 'prepare': prepare,
                'invalidate': invalidate,
            })
            connection.settimeout(0.25)
            response = receive_message(
                connection, self.monitor,
                timeout=PING_TIMEOUT if items is None else REQUEST_TIMEOUT)
        if response.get('unavailable'):
            raise DetailsServiceUnavailable(response['error'])
        if response.get('error'):
            raise DetailsServiceError(response['error'])
        result = response['items']
        if not isinstance(result, list) or (items is not None and len(result) != len(items)):
            raise DetailsServiceUnavailable('Incomplete item detail service response')
        self.log_item_errors(response.get('errors') or {})
        self.add_timings(response.get('timings') or {})
        return result

    @staticmethod
    def log_item_errors(errors):
        for error in errors.values():
            kodi_log(f'Item detail lookup failed: {error}', 1)

    def add_timings(self, timings):
        for name, seconds in timings.items():
            self.timings[name] = self.timings.get(name, 0) + seconds

    @contextmanager
    def measure(self, name):
        started = perf_counter()
        try:
            yield
        finally:
            self.add_timings({name: perf_counter() - started})

    def is_current(self, endpoint):
        return bool(endpoint) and endpoint.get('version') == self.version

    def is_healthy(self, endpoint):
        try:
            self.exchange(endpoint)
        except (OSError, DetailsServiceUnavailable):
            return False
        return True

    def start(self):
        """Start the service if it is not running, without waiting for it."""
        if self.is_current(self.location.endpoint):
            return
        executebuiltin(RUNSCRIPT.format('details_service'))

    def get_endpoint(self, failed_endpoint=None):
        with SQLiteMutex(f'{self.location.name}.Startup', timeout=90) as mutex:
            if mutex.lockstate == -1:
                raise DetailsServiceUnavailable('Unable to start item detail service')
            endpoint = self.location.endpoint
            if self.is_current(endpoint) and endpoint != failed_endpoint and self.is_healthy(endpoint):
                return endpoint
            if endpoint:
                self.location.restart = endpoint['token']
            # Keep the invocation associated with the add-on for provider imports
            # and Monitor settings notifications on every Kodi platform.
            executebuiltin(RUNSCRIPT.format('details_service'))
            deadline = monotonic() + 60
            while not self.monitor.abortRequested() and monotonic() < deadline:
                endpoint = self.location.endpoint
                if self.is_current(endpoint) and endpoint != failed_endpoint and self.is_healthy(endpoint):
                    return endpoint
                if self.monitor.waitForAbort(0.1):
                    break
        raise DetailsServiceUnavailable('Item detail service did not become ready')

    def get_current_endpoint(self):
        endpoint = self.location.endpoint
        if self.is_current(endpoint):
            return endpoint
        return self.get_endpoint()

    def get_retry_endpoint(self, endpoint):
        """Only restart the service when it no longer answers a ping."""
        if self.is_healthy(endpoint):
            return endpoint
        return self.get_endpoint(failed_endpoint=endpoint)

    def get_batch_items(self, entries, kodi_details=False):
        # Waiting for the service to start or answer is timed as boot.
        with self.measure('boot'):
            endpoint = self.get_current_endpoint()
        try:
            return self.exchange(endpoint, entries, kodi_details)
        except (OSError, DetailsServiceUnavailable):
            if self.monitor.abortRequested():
                raise
        with self.measure('boot'):
            endpoint = self.get_retry_endpoint(endpoint)
        return self.exchange(endpoint, entries, kodi_details)

    def get_batch(self, entries, kodi_details=False):
        try:
            return self.get_batch_items(entries, kodi_details)
        except (OSError, DetailsServiceError) as exc:
            kodi_log(f'Item detail service request failed: {exc}', 1)
            return [None for _ in entries]

    @staticmethod
    def get_entries(requests, items=None):
        """Pair each request with the list item data to merge its details into.
        Requests without list item data are answered with the details alone.
        A None request sends list item data for Kodi library matching only."""
        items = items or [None for _ in requests]
        return [
            {'request': request.as_dict() if request else None, 'item': item}
            for request, item in zip(requests, items)
        ]

    def get_items(self, requests, items=None, kodi_details=False):
        entries = self.get_entries(requests, items)
        return [
            item
            for offset in range(0, len(entries), MAX_REQUEST_ITEMS)
            for item in self.get_batch(entries[offset:offset + MAX_REQUEST_ITEMS], kodi_details)
        ]

    def get_item(self, request):
        return self.get_items([request])[0]

    def prepare(self, info=None, tmdb_type=None):
        """Ask a running service to start refreshing synced play data while the list is
        retrieved. A stopped service is not started here so the list is not held up; the
        item details request refreshes the data instead."""
        endpoint = self.location.endpoint
        if not self.is_current(endpoint):
            return
        try:
            self.exchange(endpoint, prepare={'info': info, 'tmdb_type': tmdb_type})
        except (OSError, DetailsServiceError) as exc:
            kodi_log(f'Item detail sync refresh was not started early: {exc}', 1)

    def invalidate(self):
        """Clear assembled metadata after item details were changed outside the service.
        A running service clears its memory and stored copies. Otherwise the stored copies
        are cleared here, without starting the service, so that no later start reuses them."""
        endpoint = self.location.endpoint
        if self.is_current(endpoint) and self.request_invalidate(endpoint):
            return
        self.clear_stored_metadata()

    def request_invalidate(self, endpoint):
        try:
            self.exchange(endpoint, invalidate=True)
        except (OSError, DetailsServiceError) as exc:
            kodi_log(f'Item detail service did not clear metadata, clearing stored copies: {exc}', 1)
            return False
        return True

    @staticmethod
    def clear_stored_metadata():
        from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
        from tmdbhelper.lib.items.database.details.storedmetadata import DetailsStoredMetadata
        DetailsStoredMetadata(ItemDetailsDatabase()).clear()
