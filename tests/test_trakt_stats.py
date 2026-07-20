import functools
import pathlib
import runpy
import sys
import types
import unittest


class TestGetTraktStatsRequest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ftools = types.ModuleType('jurialmunkey.ftools')
        setattr(ftools, 'cached_property', functools.cached_property)
        package = types.ModuleType('jurialmunkey')
        setattr(package, 'ftools', ftools)
        sys.modules['jurialmunkey'] = package
        sys.modules['jurialmunkey.ftools'] = ftools

        path = pathlib.Path(
            'resources/tmdbhelper/lib/query/database/trakt_stats.py')
        cls.request_type = runpy.run_path(str(path))['GetTraktStatsRequest']

    def test_items_ignores_non_mapping_response_values(self):
        request = object.__new__(self.request_type)
        request.__dict__['response_json'] = {
            'movies': {'watched': 3, 'collected': 2},
            'account': 'jsox79',
        }

        self.assertEqual(request.items, [
            {'name': 'watched', 'type': 'movies', 'stat': 3},
            {'name': 'collected', 'type': 'movies', 'stat': 2},
        ])


if __name__ == '__main__':
    unittest.main()
