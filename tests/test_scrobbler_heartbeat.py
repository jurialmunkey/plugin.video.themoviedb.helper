import functools
import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


ROOT = pathlib.Path(__file__).parents[1]
SCROBBLER_PATH = ROOT / "resources" / "tmdbhelper" / "lib" / "monitor" / "scrobbler.py"


def stub_module(name, **attributes):
    module = types.ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    sys.modules[name] = module


stub_module("jurialmunkey")
stub_module("jurialmunkey.window", get_property=lambda *args, **kwargs: 1)
stub_module("jurialmunkey.ftools", cached_property=functools.cached_property)
stub_module("jurialmunkey.parser", try_int=int)
stub_module("tmdbhelper")
stub_module("tmdbhelper.lib")
stub_module("tmdbhelper.lib.addon")
stub_module("tmdbhelper.lib.addon.plugin", get_setting=lambda *args, **kwargs: True)
stub_module("tmdbhelper.lib.addon.logger", kodi_log=lambda *args, **kwargs: None)
stub_module("tmdbhelper.lib.addon.tmdate", set_timestamp=lambda value=0: value)


class DeferredThread:
    instances = []

    def __init__(self, target):
        self.target = target
        self.started = False
        self.joined = False
        self.instances.append(self)

    def start(self):
        self.started = True

    def join(self, timeout=None):
        self.joined = True


stub_module("tmdbhelper.lib.addon.thread", SafeThread=DeferredThread)

spec = importlib.util.spec_from_file_location("heartbeat_scrobbler", SCROBBLER_PATH)
scrobbler_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scrobbler_module)
PlayerScrobbler = scrobbler_module.PlayerScrobbler


class HeartbeatScrobbler(PlayerScrobbler):
    def __init__(self):
        self.tmdb_type = "movie"
        self.tmdb_id = 1081003
        self.total_time = 6000
        self.started = True
        self.stopped = False
        self.syncing = False
        self._heartbeat_inflight = False
        self._heartbeat_last = 1000
        self._heartbeat_thread = None
        self.scrobble = Mock()


class TestHeartbeat(unittest.TestCase):
    def setUp(self):
        DeferredThread.instances.clear()
        self.scrobbler = HeartbeatScrobbler()

    @patch.object(scrobbler_module, "monotonic", return_value=1299)
    def test_does_not_send_before_interval(self, _monotonic):
        self.assertFalse(self.scrobbler.heartbeat("movie", 1081003))
        self.scrobbler.scrobble.assert_not_called()
        self.assertEqual([], DeferredThread.instances)

    @patch.object(scrobbler_module, "monotonic", return_value=1300)
    def test_schedules_background_heartbeat_at_interval(self, _monotonic):
        self.assertTrue(self.scrobbler.heartbeat("movie", 1081003))
        self.assertEqual(1, len(DeferredThread.instances))
        self.assertTrue(DeferredThread.instances[0].started)
        self.assertTrue(self.scrobbler._heartbeat_inflight)
        self.scrobbler.scrobble.assert_not_called()

    @patch.object(scrobbler_module, "monotonic", return_value=1600)
    def test_allows_only_one_inflight_request(self, _monotonic):
        self.assertTrue(self.scrobbler.heartbeat("movie", 1081003))
        self.assertFalse(self.scrobbler.heartbeat("movie", 1081003))
        self.assertEqual(1, len(DeferredThread.instances))

    @patch.object(scrobbler_module, "monotonic", return_value=1300)
    def test_worker_sends_start_and_releases_inflight_guard(self, _monotonic):
        self.assertTrue(self.scrobbler.heartbeat("movie", 1081003))
        DeferredThread.instances[0].target()
        self.scrobbler.scrobble.assert_called_once_with("start")
        self.assertFalse(self.scrobbler._heartbeat_inflight)

    @patch.object(scrobbler_module, "monotonic", return_value=1300)
    def test_shutdown_can_wait_for_inflight_heartbeat(self, _monotonic):
        self.assertTrue(self.scrobbler.heartbeat("movie", 1081003))
        self.scrobbler.wait_for_heartbeat(timeout=3)
        self.assertTrue(DeferredThread.instances[0].joined)

    @patch.object(scrobbler_module, "monotonic", return_value=1001)
    def test_force_flush_runs_synchronously(self, _monotonic):
        self.assertTrue(self.scrobbler.heartbeat("movie", 1081003, force=True, background=False))
        self.scrobbler.scrobble.assert_called_once_with("start")
        self.assertFalse(self.scrobbler._heartbeat_inflight)
        self.assertEqual([], DeferredThread.instances)

    @patch.object(scrobbler_module, "monotonic", return_value=1600)
    def test_stopped_or_synced_playback_never_heartbeats(self, _monotonic):
        self.scrobbler.stopped = True
        self.assertFalse(self.scrobbler.heartbeat("movie", 1081003))
        self.scrobbler.stopped = False
        self.scrobbler.syncing = True
        self.assertFalse(self.scrobbler.heartbeat("movie", 1081003))
        self.scrobbler.scrobble.assert_not_called()

    @patch.object(scrobbler_module, "monotonic", return_value=1600)
    def test_mismatched_item_never_heartbeats(self, _monotonic):
        self.assertFalse(self.scrobbler.heartbeat("movie", 999))
        self.scrobbler.scrobble.assert_not_called()


if __name__ == "__main__":
    unittest.main()
