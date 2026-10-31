import socket
from time import monotonic
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

    def exchange(self, endpoint, items=None):
        with socket.create_connection(('127.0.0.1', endpoint['port']), timeout=2) as connection:
            connection.settimeout(5)
            send_message(connection, {
                'version': PROTOCOL_VERSION, 'token': endpoint['token'],
                'items': items,
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
        return result

    @staticmethod
    def log_item_errors(errors):
        for error in errors.values():
            kodi_log(f'Item detail lookup failed: {error}', 1)

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

    def get_batch_items(self, requests):
        items = [request.as_dict() for request in requests]
        endpoint = self.get_current_endpoint()
        try:
            return self.exchange(endpoint, items)
        except (OSError, DetailsServiceUnavailable):
            if self.monitor.abortRequested():
                raise
        return self.exchange(self.get_retry_endpoint(endpoint), items)

    def get_batch(self, requests):
        try:
            return self.get_batch_items(requests)
        except (OSError, DetailsServiceError) as exc:
            kodi_log(f'Item detail service request failed: {exc}', 1)
            return [None for _ in requests]

    def get_items(self, requests):
        return [
            item
            for offset in range(0, len(requests), MAX_REQUEST_ITEMS)
            for item in self.get_batch(requests[offset:offset + MAX_REQUEST_ITEMS])
        ]

    def get_item(self, request):
        return self.get_items([request])[0]
