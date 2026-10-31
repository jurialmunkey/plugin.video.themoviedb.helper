import traceback
from concurrent.futures import TimeoutError as FutureTimeoutError
from secrets import token_hex
from socketserver import BaseRequestHandler, ThreadingMixIn, TCPServer
from threading import Event, Thread
from time import monotonic
from xbmc import Monitor
from xbmcaddon import Addon
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.plugin import get_version
from tmdbhelper.lib.files.sqlite_mutex import SQLiteMutex
from tmdbhelper.lib.items.database.details.coordinator import DetailsCoordinator
from tmdbhelper.lib.items.database.details.protocol import (
    DetailsLookupError, DetailsServiceError, DetailsServiceUnavailable,
    MAX_REQUEST_ITEMS, PROTOCOL_VERSION, RESPONSE_TIMEOUT, ServiceLocation,
    encode_message, receive_message,
)
from tmdbhelper.lib.items.database.details.request import DetailsRequest
from tmdbhelper.lib.items.database.details.settings import DetailsSettings


class DetailsMonitor(Monitor):
    def __init__(self):
        super().__init__()
        self.settings_changed = Event()

    def onSettingsChanged(self):
        self.settings_changed.set()


class DetailsRequestHandler(BaseRequestHandler):
    def handle(self):
        self.request.settimeout(0.25)
        try:
            message = receive_message(self.request, self.server.monitor, timeout=10)
            response = self.get_response(message)
        except DetailsServiceUnavailable as exc:
            response = {'error': str(exc), 'unavailable': True}
        except (DetailsServiceError, TypeError, ValueError, KeyError) as exc:
            response = {'error': str(exc)}
        except OSError:
            return
        self.request.settimeout(5)
        try:
            self.request.sendall(self.get_encoded_response(response))
        except OSError:
            return  # The requesting widget may have been closed.

    @staticmethod
    def get_encoded_response(response):
        try:
            return encode_message(response)
        except DetailsServiceError as exc:
            # Report oversize responses as a request error, not a dropped connection,
            # so that the client does not mistake it for a failed service.
            return encode_message({'error': str(exc)})

    def get_response(self, message):
        if message['version'] != PROTOCOL_VERSION or message['token'] != self.server.token:
            raise DetailsServiceUnavailable('Item detail service protocol/token mismatch')
        items = message['items']
        if items is None:
            if not self.server.coordinator.is_alive() or self.server.coordinator.stopping:
                raise DetailsServiceUnavailable('Item detail coordinator stopped')
            return {'items': []}
        if not isinstance(items, list) or len(items) > MAX_REQUEST_ITEMS:
            raise DetailsServiceError('Invalid item detail batch')
        requests = [DetailsRequest(**item) for item in items]
        futures = self.server.coordinator.submit(requests)
        deadline = monotonic() + RESPONSE_TIMEOUT
        results = [self.get_result(future, deadline) for future in futures]
        return {
            'items': [item for item, error in results],
            'errors': {f'{x}': error for x, (item, error) in enumerate(results) if error},
        }

    @staticmethod
    def get_result(future, deadline):
        try:
            return (future.result(timeout=max(deadline - monotonic(), 0)), None)
        except DetailsLookupError as exc:
            return (None, str(exc))
        except FutureTimeoutError:
            raise DetailsServiceError('Item detail lookup timed out')


class DetailsServer(ThreadingMixIn, TCPServer):
    request_queue_size = 128
    allow_reuse_address = True

    def __init__(self, coordinator, monitor):
        self.coordinator = coordinator
        self.monitor = monitor
        self.token = token_hex(24)
        super().__init__(('127.0.0.1', 0), DetailsRequestHandler)

    def handle_error(self, request, client_address):
        kodi_log(f'Item detail transport error:\n{traceback.format_exc()}', 1)


class DetailsService:
    def __init__(self):
        self.monitor = DetailsMonitor()
        self.location = ServiceLocation()
        self.settings = DetailsSettings()
        self.version = get_version()

    @property
    def is_outdated(self):
        """The add-on was updated while this script kept running the old code."""
        return Addon().getAddonInfo('version') != self.version

    def run(self):
        # Wait briefly so a replacement started during an outdated instance's exit
        # still acquires the lock once the old instance releases it.
        with SQLiteMutex(f'{self.location.name}.Instance', timeout=10) as mutex:
            if mutex.lockstate == -1:
                return
            while not self.monitor.abortRequested() and not self.is_outdated:
                try:
                    self.run_instance()
                except Exception:
                    kodi_log(f'Item detail service failed:\n{traceback.format_exc()}', 1)
                if self.monitor.waitForAbort(1):
                    break

    def run_instance(self):
        coordinator = DetailsCoordinator()
        server = DetailsServer(coordinator, self.monitor)
        listener = Thread(target=server.serve_forever, name='TMDbHelper detail listener')
        try:
            self.monitor.settings_changed.clear()
            settings = self.settings.get_snapshot()
            coordinator.start()
            listener.start()
            self.location.endpoint = {
                'port': server.server_address[1], 'token': server.token,
                'version': self.version}
            while not self.monitor.waitForAbort(1):
                if self.location.restart == server.token:
                    break
                if self.is_settings_changed(settings):
                    break
                if not coordinator.is_alive() or not listener.is_alive():
                    raise DetailsServiceUnavailable(f'Item detail worker stopped: {coordinator.failure}')
        finally:
            endpoint = self.location.endpoint
            if endpoint and endpoint['token'] == server.token:
                self.location.endpoint = None
            if listener.is_alive():
                server.shutdown()
                listener.join()
            if coordinator.ident is not None:
                coordinator.stop()
            server.server_close()

    def is_settings_changed(self, settings):
        if not self.monitor.settings_changed.is_set():
            return False
        self.monitor.settings_changed.clear()
        return self.settings.get_snapshot() != settings
