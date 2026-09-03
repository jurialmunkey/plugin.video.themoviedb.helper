#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property


class TraktSyncDataGetterAllUnHiddenShowsInProgress:
    calendar_startdate = -14
    calendar_days = 15
    additional_keys = ()

    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata

    @property
    def get_episode_watchedcount(self):
        return self.instance_syncdata.get_episode_watchedcount

    @property
    def get_episode_playcount(self):
        return self.instance_syncdata.get_episode_playcount

    @cached_property
    def calendar_data(self):
        return self.get_calendar_data()

    def get_calendar_data(self):
        from tmdbhelper.lib.items.directories.trakt.lists_calendar import ListTraktCalendarProperties
        list_properties = ListTraktCalendarProperties()
        list_properties.trakt_api = self.instance_syncdata.trakt_api
        list_properties.trakt_date = self.calendar_startdate
        list_properties.trakt_days = self.calendar_days
        list_properties.trakt_type = 'episode'
        return list_properties.api_response_json

    @cached_property
    def calendar_episodes(self):
        return self.get_calendar_episodes()

    def get_calendar_episodes(self):
        from tmdbhelper.lib.addon.tmdate import date_in_range
        from tmdbhelper.lib.addon.plugin import get_setting

        if not get_setting('nextepisodes_usecalendar'):
            return

        if not self.calendar_data:
            return

        calendar = {}

        for i in self.calendar_data:
            try:
                # Check that date is still in range once utc_converted
                if not date_in_range(
                    i['first_aired'],
                    utc_convert=True,
                    start_date=self.calendar_startdate,
                    days=self.calendar_days
                ):
                    continue

                # Ignore specials
                if i['episode']['season'] == 0:
                    continue

                show = calendar.setdefault(i['show']['ids']['tmdb'], {})
                show.setdefault(i['episode']['season'], []).append(i['episode']['number'])

            except KeyError:
                continue

        return calendar

    def is_calendar_watched(self, tmdb_id):
        if not self.calendar_episodes:
            return True
        if tmdb_id not in self.calendar_episodes:
            return True
        for season in self.calendar_episodes[tmdb_id]:
            # Check for a new season airing
            if not self.get_episode_watchedcount(tmdb_id, season):
                return False
            # Check for a new episode airing
            for episode in self.calendar_episodes[tmdb_id][season]:
                if not self.get_episode_playcount(tmdb_id, season, episode):
                    return False
        return True

    def is_inprogress_show(self, tmdb_id, aired_episodes, watched_episodes):
        if aired_episodes <= watched_episodes:
            if self.is_calendar_watched(tmdb_id):
                return False
        return True

    @cached_property
    def parent_getter(self):
        return self.get_parent_getter()

    def get_parent_getter(self):
        sd = self.instance_syncdata.get_all_unhidden_shows_started_getter()
        sd.additional_keys = self.parent_additional_keys
        return sd

    @cached_property
    def keys(self):
        return self.get_keys()

    def get_keys(self):
        return self.parent_getter.keys

    @property
    def parent_additional_keys(self):
        return ('aired_episodes', 'watched_episodes', 'dropped_hidden_at', 'last_watched_at', *(self.additional_keys or ()))

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        sd = self.parent_getter
        return [
            i for i in sd.items
            if self.is_inprogress_show(
                i['tmdb_id'],
                i['aired_episodes'],
                i['watched_episodes']
            )
        ]
