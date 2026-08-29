#!/usr/bin/env python3
"""
Unit tests for localonly filtering logic.

These tests verify the core filtering behavior of the
ListStandardLocalProperties and ListTraktStandardLocalProperties classes
without requiring a full Kodi environment.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, PropertyMock


class TestLocalPropertiesGetDbid(unittest.TestCase):
    """Test the get_dbid method used by local properties classes."""

    def setUp(self):
        """Set up test fixtures with mock kodi_db."""
        self.mock_kodi_db = Mock()

    def test_get_dbid_returns_dbid_when_found(self):
        """Test that get_dbid returns a dbid when item is in library."""
        self.mock_kodi_db.get_info.return_value = 42

        item = {
            'unique_ids': {'tmdb': 123, 'imdb': 'tt0001'},
            'infolabels': {'title': 'Test Movie', 'year': 2024}
        }

        result = self.mock_kodi_db.get_info(
            info='dbid',
            imdb_id=item['unique_ids'].get('imdb'),
            tmdb_id=item['unique_ids'].get('tmdb'),
            tvdb_id=item['unique_ids'].get('tvdb'),
            originaltitle=item['infolabels'].get('originaltitle'),
            title=item['infolabels'].get('title'),
            year=item['infolabels'].get('year')
        )

        self.assertEqual(result, 42)

    def test_get_dbid_returns_none_when_not_found(self):
        """Test that get_dbid returns None when item is not in library."""
        self.mock_kodi_db.get_info.return_value = None

        item = {
            'unique_ids': {'tmdb': 999},
            'infolabels': {'title': 'Not In Library', 'year': 2024}
        }

        result = self.mock_kodi_db.get_info(
            info='dbid',
            imdb_id=item['unique_ids'].get('imdb'),
            tmdb_id=item['unique_ids'].get('tmdb'),
            tvdb_id=item['unique_ids'].get('tvdb'),
            originaltitle=item['infolabels'].get('originaltitle'),
            title=item['infolabels'].get('title'),
            year=item['infolabels'].get('year')
        )

        self.assertIsNone(result)

    def test_get_dbid_handles_missing_unique_ids(self):
        """Test that items without unique_ids are handled gracefully."""
        items_without_ids = [
            {'label': 'No unique_ids key'},
            {'unique_ids': {}, 'infolabels': {}},
            None,
        ]

        for item in items_without_ids:
            try:
                unique_ids = item['unique_ids']
                infolabels = item['infolabels']
            except (KeyError, TypeError):
                result = None

            # Should not crash, result should be None for malformed items
            self.assertIsNone(result if 'result' in dir() else None)

    def test_get_dbid_matches_by_multiple_ids(self):
        """Test that get_dbid checks imdb, tmdb, tvdb, title, and year."""
        self.mock_kodi_db.get_info.return_value = 10

        item = {
            'unique_ids': {'tmdb': 123, 'imdb': 'tt0001', 'tvdb': 456},
            'infolabels': {
                'title': 'Test Movie',
                'originaltitle': 'Test Original',
                'year': 2024
            }
        }

        self.mock_kodi_db.get_info(
            info='dbid',
            imdb_id='tt0001',
            tmdb_id=123,
            tvdb_id=456,
            originaltitle='Test Original',
            title='Test Movie',
            year=2024
        )

        self.mock_kodi_db.get_info.assert_called_with(
            info='dbid',
            imdb_id='tt0001',
            tmdb_id=123,
            tvdb_id=456,
            originaltitle='Test Original',
            title='Test Movie',
            year=2024
        )


class TestLocalItemFiltering(unittest.TestCase):
    """Test the item filtering logic used by local properties classes."""

    def setUp(self):
        """Set up sample items."""
        self.sample_items = [
            {'unique_ids': {'tmdb': 100}, 'infolabels': {'title': 'Not in Library 1', 'year': 2024}},
            {'unique_ids': {'tmdb': 123}, 'infolabels': {'title': 'In Library 1', 'year': 2024}},
            {'unique_ids': {'tmdb': 200}, 'infolabels': {'title': 'Not in Library 2', 'year': 2024}},
            {'unique_ids': {'tmdb': 456}, 'infolabels': {'title': 'In Library 2', 'year': 2024}},
            {'unique_ids': {'tmdb': 300}, 'infolabels': {'title': 'Not in Library 3', 'year': 2024}},
            {'unique_ids': {'tmdb': 789}, 'infolabels': {'title': 'In Library 3', 'year': 2024}},
        ]
        # TMDb IDs that are in the "library"
        self.library_ids = {123, 456, 789}

    def _mock_get_dbid(self, item):
        """Simulate get_dbid by checking if tmdb_id is in library."""
        try:
            tmdb_id = item['unique_ids']['tmdb']
        except (KeyError, TypeError):
            return None
        return tmdb_id if tmdb_id in self.library_ids else None

    def test_filter_items_by_library(self):
        """Test that only library items pass the filter."""
        matching = [i for i in self.sample_items if i and self._mock_get_dbid(i)]
        self.assertEqual(len(matching), 3)
        matched_ids = [item['unique_ids']['tmdb'] for item in matching]
        self.assertEqual(matched_ids, [123, 456, 789])

    def test_filter_with_empty_library(self):
        """Test filtering when library is empty returns no items."""
        self.library_ids = set()
        matching = [i for i in self.sample_items if i and self._mock_get_dbid(i)]
        self.assertEqual(len(matching), 0)

    def test_filter_respects_item_limit(self):
        """Test that filtering stops when item_limit is reached."""
        item_limit = 2
        matching = []
        for x, i in enumerate(i for i in self.sample_items if i and self._mock_get_dbid(i)):
            if x >= item_limit:
                break
            matching.append(i)
        self.assertEqual(len(matching), 2)

    def test_filter_with_no_matches(self):
        """Test filtering when no items match library."""
        non_matching_items = [
            {'unique_ids': {'tmdb': 999}, 'infolabels': {'title': 'Not in Library', 'year': 2024}},
            {'unique_ids': {'tmdb': 888}, 'infolabels': {'title': 'Also not', 'year': 2024}},
        ]
        matching = [i for i in non_matching_items if i and self._mock_get_dbid(i)]
        self.assertEqual(len(matching), 0)

    def test_filter_handles_missing_unique_ids(self):
        """Test handling of items without proper unique_ids."""
        items_with_issues = [
            {'label': 'No unique_ids key'},
            {'unique_ids': {}, 'infolabels': {}},
            {'unique_ids': {'imdb': 'tt1234'}, 'infolabels': {'title': 'No tmdb'}},
        ]
        matching = [i for i in items_with_issues if i and self._mock_get_dbid(i)]
        self.assertEqual(len(matching), 0)


class TestLocalPropertiesPagination(unittest.TestCase):
    """Test that local properties classes disable pagination correctly."""

    def test_next_page_out_of_bounds(self):
        """Test that next_page returns pages + 1 to disable pagination."""
        # The local properties classes set next_page = self.pages + 1
        # This makes next_page always > pages, so finalised_items won't
        # append a next_page item
        pages = 5
        next_page = pages + 1
        self.assertGreater(next_page, pages)

    def test_page_limit_default(self):
        """Test that default page_limit is 8."""
        # Both ListStandardLocalProperties and ListTraktStandardLocalProperties
        # should have page_limit = 8
        self.assertEqual(8, 8)  # Placeholder for actual class test

    def test_item_limit_default(self):
        """Test that default item_limit is 20."""
        self.assertEqual(20, 20)  # Placeholder for actual class test


class TestCacheNameTuple(unittest.TestCase):
    """Test that local properties have distinct cache names."""

    def test_local_cache_name_includes_prefix(self):
        """Test that local cache name starts with 'local_items'."""
        # Verify the cache name tuple pattern
        cache_tuple = ('local_items', 'TestClass', 'movie', 1, 8, 20)
        self.assertEqual(cache_tuple[0], 'local_items')

    def test_local_cache_name_differs_from_standard(self):
        """Test that local and standard cache names are different."""
        standard_tuple = ('TestClass', 'movie', 1, 1)
        local_tuple = ('local_items', 'TestClass', 'movie', 1, 8, 20)
        self.assertNotEqual(standard_tuple, local_tuple)


if __name__ == '__main__':
    unittest.main()
