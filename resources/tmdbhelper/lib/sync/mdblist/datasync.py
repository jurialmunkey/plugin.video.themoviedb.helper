#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property


class MDbListSyncDataGetterAllUnHiddenShowsInProgress:
    additional_keys = ()

    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata

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

    def is_inprogress(self, item):
        if not item['aired_episodes']:
            return False
        if not item['watched_episodes']:
            return True
        if item['aired_episodes'] > item['watched_episodes']:
            return True
        return False

    def get_items(self):
        sd = self.parent_getter
        return [i for i in sd.items if self.is_inprogress(i)]
