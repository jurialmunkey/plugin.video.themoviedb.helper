import socket
from time import monotonic
from xbmc import Monitor
from tmdbhelper.lib.addon.consts import RUNSCRIPT
from tmdbhelper.lib.addon.plugin import executebuiltin
from tmdbhelper.lib.files.sqlite_mutex import SQLiteMutex
from tmdbhelper.lib.items.database.details.protocol import (
    DetailsServiceError, DetailsServiceUnavailable, MAX_REQUEST_ITEMS,
    PROTOCOL_VERSION, ServiceLocation, receive_message, send_message,
)


class DetailsClient:
    def __init__(self):
        self.monitor = Monitor()
        self.location = ServiceLocation()

    def exchange(self, endpoint, items=None):
        with socket.create_connection(('127.0.0.1', endpoint['port']), timeout=2) as connection:
            connection.settimeout(5)
            send_message(connection, {
                'version': PROTOCOL_VERSION, 'token': endpoint['token'],
                'items': items,
            })
            connection.settimeout(0.25)
            response = receive_message(connection, self.monitor, timeout=5 if items is None else 300)
        if response.get('unavailable'):
            raise DetailsServiceUnavailable(response['error'])
        if response.get('error'):
            raise DetailsServiceError(response['error'])
        result = response['items']
        if not isinstance(result, list) or (items is not None and len(result) != len(items)):
            raise DetailsServiceUnavailable('Incomplete item detail service response')
        return result

    def get_endpoint(self, failed_endpoint=None):
        with SQLiteMutex(f'{self.location.name}.Startup', timeout=90) as mutex:
            if mutex.lockstate == -1:
                raise DetailsServiceUnavailable('Unable to start item detail service')
            endpoint = self.location.endpoint
            if endpoint and endpoint != failed_endpoint:
                try:
                    self.exchange(endpoint)
                    return endpoint
                except (OSError, DetailsServiceUnavailable):
                    failed_endpoint = endpoint
            if endpoint:
                self.location.restart = endpoint['token']
            # Keep the invocation associated with the add-on for provider imports
            # and Monitor settings notifications on every Kodi platform.
            executebuiltin(RUNSCRIPT.format('details_service'))
            deadline = monotonic() + 60
            while not self.monitor.abortRequested() and monotonic() < deadline:
                endpoint = self.location.endpoint
                if endpoint and endpoint != failed_endpoint:
                    try:
                        self.exchange(endpoint)
                        return endpoint
                    except (OSError, DetailsServiceUnavailable):
                        pass
                if self.monitor.waitForAbort(0.1):
                    break
        raise DetailsServiceUnavailable('Item detail service did not become ready')

    def get_items(self, requests):
        if not requests:
            return []
        if len(requests) > MAX_REQUEST_ITEMS:
            return [
                item
                for offset in range(0, len(requests), MAX_REQUEST_ITEMS)
                for item in self.get_items(requests[offset:offset + MAX_REQUEST_ITEMS])
            ]
        items = [request.as_dict() for request in requests]
        endpoint = self.location.endpoint or self.get_endpoint()
        for attempt in range(2):
            try:
                return self.exchange(endpoint, items)
            except (OSError, DetailsServiceUnavailable):
                if self.monitor.abortRequested() or attempt:
                    raise
                endpoint = self.get_endpoint(failed_endpoint=endpoint)

    def get_item(self, request):
        return self.get_items([request])[0]
