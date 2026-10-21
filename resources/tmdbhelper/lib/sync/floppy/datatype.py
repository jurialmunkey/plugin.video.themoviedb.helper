from tmdbhelper.lib.sync.datatype import DataType, DataTypeEpisodesInShows, DataTypeShowsToEpisodes


class FloppyDataType(DataType):
    # Floppy tracks some shows in a separate anime library so shows are read from both
    floppy_media_types = {'movie': ('movie', ), 'show': ('tv', 'anime', ), 'season': ('season', ), 'episode': ('episode', )}
    record_list_class = None

    @property
    def tracking_status_param(self):
        """ Server side filter matching the client side statuses of the record list """
        try:
            return ','.join(str(i) for i in self.record_list_class.tracking_statuses)
        except TypeError:  # No status filter
            return

    @property
    def sync_args(self):
        """ Request paths for the item type """
        return tuple(('media', i, ) for i in self.floppy_media_types[self.item_type])

    @property
    def sync_kwgs(self):
        return {'source': 'tmdb', 'status': self.tracking_status_param}

    def get_syncitem(self, meta):
        from tmdbhelper.lib.sync.floppy.itemdata import FloppySyncItem
        return FloppySyncItem(self.item_type, meta, self.keys, key_prefix=self.key_prefix)

    def get_response_sync_data(self, *args, **kwargs):
        if not self.floppy_api:
            return
        return self.floppy_api.get_paginated_results(*args, **kwargs)

    def get_response_sync_entries(self, *paths, **kwargs):
        """ Entries from every path or None if any path failed """
        results = [self.get_response_sync_data(*path, **kwargs) for path in paths]
        if None in results:
            return
        return [j for i in results for j in i]

    def get_response_sync(self, *paths, **kwargs):
        entries = self.get_response_sync_entries(*paths, **kwargs)
        if entries is None:
            return
        return self.record_list_class(entries, self.item_type).data


class FloppyDataTypeEpisodesInShows(DataTypeEpisodesInShows, FloppyDataType):
    pass


class FloppyDataTypeShowsToEpisodes(DataTypeShowsToEpisodes, FloppyDataType):
    pass


class FloppyDataTypeNull(FloppyDataType):  # NullType for when no corresponding Floppy data for sync

    keys = tuple()
    tracking_status_param = None

    def clear_columns(self, keys):
        pass

    def get_response_sync(self, *args, **kwargs):
        return []
