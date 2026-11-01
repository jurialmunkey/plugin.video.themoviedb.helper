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
from tmdbhelper.lib.items.database.details.enrichment import KodiDetailsEnrichment, KodiLibraryCache
from tmdbhelper.lib.items.database.details.merge import ConfiguredItemMerger
from tmdbhelper.lib.items.database.details.protocol import (
    DetailsLookupError, DetailsServiceError, DetailsServiceUnavailable,
    MAX_REQUEST_ITEMS, PROTOCOL_VERSION, RESPONSE_TIMEOUT, ServiceLocation,
    encode_message, receive_message,
)
from tmdbhelper.lib.items.database.details.refresh import DetailsSyncRefresher
from tmdbhelper.lib.items.database.details.request import DetailsRequest
from tmdbhelper.lib.items.database.details.settings import DetailsSettings
from tmdbhelper.lib.sync.prepare import SyncPreparation


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
        if message.get('prepare') is not None:
            return self.get_prepare_response(message['prepare'])
        entries = message['items']
        if entries is None:
            if not self.server.coordinator.is_alive() or self.server.coordinator.stopping:
                raise DetailsServiceUnavailable('Item detail coordinator stopped')
            return {'items': []}
        if not isinstance(entries, list) or len(entries) > MAX_REQUEST_ITEMS:
            raise DetailsServiceError('Invalid item detail batch')
        results = [
            self.get_entry_result(entry, result)
            for entry, result in zip(entries, self.get_detail_results(entries))]
        if message.get('kodi_details'):
            results = self.get_kodi_results(entries, results)
        return {
            'items': [item for item, error in results],
            'errors': {f'{x}': error for x, (item, error) in enumerate(results) if error},
        }

    def get_prepare_response(self, prepare):
        """Start refreshing synced play data while the list is retrieved, without waiting.
        Lists send this only when they permit synced data."""
        if SyncPreparation.is_enabled():
            self.server.sync_refresher.refresh(SyncPreparation.get_hint_item_types(**prepare))
        return {'items': []}

    def get_detail_results(self, entries):
        """Details for each entry. Entries sent only for Kodi library matching have no request."""
        requests = [DetailsRequest(**entry['request']) for entry in entries if entry['request'] is not None]
        deadline = monotonic() + RESPONSE_TIMEOUT
        self.wait_for_sync(requests, deadline)
        futures = iter(self.server.coordinator.submit(requests))
        return [
            self.get_result(next(futures), deadline) if entry['request'] is not None else (None, None)
            for entry in entries]

    def wait_for_sync(self, requests, deadline):
        """Read items only once their synced play data is fresh, as lists did before building items."""
        if not SyncPreparation.is_enabled():
            return
        item_types = SyncPreparation.get_item_types(request.mediatype for request in requests if request.sync_details)
        self.server.sync_refresher.wait(item_types, timeout=max(deadline - monotonic(), 0))

    @staticmethod
    def get_result(future, deadline):
        try:
            return (future.result(timeout=max(deadline - monotonic(), 0)), None)
        except DetailsLookupError as exc:
            return (None, str(exc))
        except FutureTimeoutError:
            raise DetailsServiceError('Item detail lookup timed out')

    @staticmethod
    def get_entry_result(entry, result):
        """Merge the details into the entry's list item data, if it sent any.
        Merging runs on this handler thread so that lists do not queue behind each other."""
        details, error = result
        if not details or entry['item'] is None:
            return result
        try:
            return (ConfiguredItemMerger(entry['item'], details).merged, None)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            return (None, f'Unable to merge item details: {exc}')

    def get_kodi_results(self, entries, results):
        """Merge Kodi library details into each item, including items whose details lookup
        failed. Entries without list item data are details-only requests and are not enriched."""
        items = [
            None if entry['item'] is None else (item or entry['item'])
            for entry, (item, error) in zip(entries, results)]
        try:
            enriched = KodiDetailsEnrichment(items, self.server.kodi_library_cache).enriched
        except Exception:
            # Library matching must not cost the batch its item details.
            kodi_log(f'Kodi library details failed:\n{traceback.format_exc()}', 1)
            return results
        return [(kodi or item, error) for kodi, (item, error) in zip(enriched, results)]


class DetailsServer(ThreadingMixIn, TCPServer):
    request_queue_size = 128
    allow_reuse_address = True

    def __init__(self, coordinator, monitor):
        self.coordinator = coordinator
        self.monitor = monitor
        self.sync_refresher = DetailsSyncRefresher()
        self.kodi_library_cache = KodiLibraryCache()  # Library indexes kept between lists
        self.token = token_hex(24)
        super().__init__(('127.0.0.1', 0), DetailsRequestHandler)

    def server_close(self):
        try:
            super().server_close()
        finally:
            self.sync_refresher.close()

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
