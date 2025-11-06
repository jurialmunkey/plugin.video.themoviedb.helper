from jurialmunkey.parser import try_int
from jurialmunkey.ftools import cached_property
from xbmc import PlayList, PLAYLIST_VIDEO


class PlayerNextEpisodes:
    def __init__(self, tmdb_id, season, episode, player=None, single=False):
        self.tmdb_id = try_int(tmdb_id)
        self.season = try_int(season)
        self.episode = try_int(episode)
        self.player = player
        self.single = single

    @cached_property
    def lidc(self):
        from tmdbhelper.lib.items.database.listitem import ListItemDetails
        lidc = ListItemDetails()
        lidc.cache_refresh = 'basic'
        lidc.extendedinfo = False
        return lidc

    @cached_property
    def parent_data(self):
        from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
        sync = BaseItemFactory('tvshow')
        sync.tmdb_id = self.tmdb_id
        return sync.data

    @cached_property
    def all_episodes(self):
        from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
        # sync = BaseViewFactory('flatseasons', 'tv', self.tmdb_id)
        sync = BaseViewFactory('episodes', 'tv', self.tmdb_id, season=self.season)  # Only get current season to avoid massive playlists TODO: Make optional get more than one season / all seasons?
        return sync.data

    @cached_property
    def next_episodes(self):
        return [i for i in self.all_episodes if self.is_future_episode(i)]

    @cached_property
    def next_episode(self):
        generator = (
            i for i in self.all_episodes
            if self.is_future_episode(i)
        )
        try:
            return [next(generator)]
        except StopIteration:
            return []

    @cached_property
    def finalised_items(self):
        return self.get_finalised_items(self.configured_items)

    @cached_property
    def finalised_item(self):
        return self.get_finalised_items(self.configured_item)

    def get_finalised_items(self, items):
        return [self.finalise_item(li) for li in items if li]

    @cached_property
    def configured_items(self):
        return self.get_configured_items(self.next_episodes)

    @cached_property
    def configured_item(self):
        return self.get_configured_items(self.next_episode)

    def get_configured_items(self, items):
        return self.lidc.configure_listitems_threaded(items)

    def is_future_episode(self, i):
        s_number = try_int(i['infolabels'].get('season', -1))
        e_number = try_int(i['infolabels'].get('episode', -1))
        if s_number < self.season:
            return False
        if s_number > self.season:
            return True
        if e_number <= self.episode:
            return False
        return True

    def finalise_item(self, li):
        if self.player:
            li.params['player'] = self.player
            li.params['mode'] = 'play'
            li.params['ignore_default'] = 'true'
            li.params['allow_playlist'] = 'false'
        li.finalise()
        return li

    @cached_property
    def listitems(self):
        return self.get_listitems(self.items)

    @cached_property
    def listitem(self):
        return self.get_listitems(self.item)

    def get_listitems(self, items):
        return [li.get_listitem() for li in items if li] if items else []

    @cached_property
    def items(self):
        if not self.parent_data:
            return
        if not self.all_episodes:
            return
        if not self.next_episodes:
            return
        if not self.configured_items:
            return
        return self.finalised_items

    @cached_property
    def item(self):
        if not self.parent_data:
            return
        if not self.all_episodes:
            return
        if not self.next_episode:
            return
        if not self.configured_item:
            return
        return self.finalised_item

    @property
    def playlist(self):
        return PlayList(PLAYLIST_VIDEO)

    def update(self, forced=True, single=False, clear=True, listitem=None):
        if not forced and self.playlist.getposition() != 0:  # If position isn't 0 then the user is already playing from the queue
            return  # We don't want to clear the existing queue so let's exit early

        listitems = self.listitem if single else self.listitems

        if not listitems:
            return

        if listitem:
            listitems.insert(0, listitem)

        if clear:
            self.playlist.clear()

        for x, listitem in enumerate(listitems):  # Add all our episodes in the queue
            self.playlist.add(listitem.getPath(), listitem, index=x)

        return self.playlist
