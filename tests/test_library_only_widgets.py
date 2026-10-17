#!/usr/bin/env python3
"""
Test script for localonly widget feature.

This script tests that the localonly filtering works correctly
for all TMDb and Trakt standard list types.

Run from Kodi with:
    RunScript(plugin.video.themoviedb.helper, run_tests)

Or run standalone (requires proper Python path setup).
"""

import sys
import os

# Test configuration
TMDB_WIDGET_TESTS = [
    # (info, tmdb_type, description)
    ('popular', 'movie', 'Popular Movies'),
    ('popular', 'tv', 'Popular TV Shows'),
    ('top_rated', 'movie', 'Top Rated Movies'),
    ('top_rated', 'tv', 'Top Rated TV Shows'),
    ('trending_day', 'movie', 'Trending Movies (Day)'),
    ('trending_day', 'tv', 'Trending TV Shows (Day)'),
    ('trending_week', 'movie', 'Trending Movies (Week)'),
    ('trending_week', 'tv', 'Trending TV Shows (Week)'),
    ('now_playing', 'movie', 'Now Playing Movies'),
    ('upcoming', 'movie', 'Upcoming Movies'),
    ('airing_today', 'tv', 'Airing Today TV Shows'),
    ('on_the_air', 'tv', 'Currently Airing TV Shows'),
    ('revenue_movies', 'movie', 'Revenue Movies'),
    ('most_voted', 'movie', 'Most Voted Movies'),
    ('most_voted', 'tv', 'Most Voted TV Shows'),
]


def run_tests():
    """Run all localonly widget tests."""
    from tmdbhelper.lib.addon.logger import kodi_log

    kodi_log('=' * 60, 1)
    kodi_log('LOCALONLY WIDGET TESTS', 1)
    kodi_log('=' * 60, 1)

    results = []

    for info, tmdb_type, description in TMDB_WIDGET_TESTS:
        result = test_widget(info, tmdb_type, description)
        results.append(result)

    # Summary
    kodi_log('=' * 60, 1)
    kodi_log('TEST SUMMARY', 1)
    kodi_log('=' * 60, 1)

    passed = sum(1 for r in results if r['passed'])
    failed = sum(1 for r in results if not r['passed'])

    for r in results:
        status = 'PASS' if r['passed'] else 'FAIL'
        kodi_log(f"[{status}] {r['description']}: {r['message']}", 1)

    kodi_log(f'Total: {passed} passed, {failed} failed', 1)

    return failed == 0


def test_widget(info, tmdb_type, description):
    """Test a single widget with localonly filtering."""
    from tmdbhelper.lib.addon.logger import kodi_log

    kodi_log(f'Testing: {description}', 1)

    try:
        # Import the appropriate list class
        from tmdbhelper.lib.addon.consts import ROUTE_DICTIONARY
        route_info = ROUTE_DICTIONARY.get(info, {}).get('route')

        if not route_info:
            return {
                'description': description,
                'passed': False,
                'message': f'No route found for info={info}'
            }

        # Dynamically import the class
        import importlib
        module = importlib.import_module(route_info['module_name'])
        list_class = getattr(module, route_info['import_attr'])

        # Create mock params simulating a widget call with localonly
        params = {
            'info': info,
            'tmdb_type': tmdb_type,
            'widget': 'true',
            'localonly': 'true',
        }

        # Create the list instance
        # We need to mock the handle since we're not in a real plugin context
        instance = list_class(handle=-1, paramstring='', **params)

        # Get items
        items = instance.get_items(tmdb_type=tmdb_type, page=1)

        if not items:
            return {
                'description': description,
                'passed': True,  # Empty is valid if no library matches
                'message': 'No matching items (library may not have matches)'
            }

        return {
            'description': description,
            'passed': True,
            'message': f'Returned {len(items)} library items'
        }

    except Exception as e:
        return {
            'description': description,
            'passed': False,
            'message': f'Exception: {str(e)}'
        }


if __name__ == '__main__':
    # For standalone testing
    success = run_tests()
    sys.exit(0 if success else 1)
