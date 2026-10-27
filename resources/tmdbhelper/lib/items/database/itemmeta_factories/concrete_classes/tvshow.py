from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.tmdate import is_unaired_timestamp
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseroutes import MediaItemInfoLabelItemRoutes, MediaItemInfoPropertyItemRoutes


class Tvshow(MediaItem):
    infolabels_dbcitem_routes = (
        MediaItemInfoLabelItemRoutes.certification,
        MediaItemInfoLabelItemRoutes.trailer,
        MediaItemInfoLabelItemRoutes.imdbnumber,
        MediaItemInfoLabelItemRoutes.english_plot,
    )

    @property
    def infolabels_dbclist_routes(self):
        return (
            *super().infolabels_dbclist_routes,
            MediaItemInfoLabelItemRoutes.network,
        )

    infoproperties_dbcitem_routes = (
        MediaItemInfoPropertyItemRoutes.watchedcount,
        MediaItemInfoPropertyItemRoutes.episodecount,
    )

    infoproperties_dbclist_routes = (
        *MediaItem.infoproperties_dbclist_routes,
        {
            'instance': ('network', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'icon': 'logo', 'country': 'country'},
            'propname': ('network', ),
            'joinings': None
        }
    )

    def get_infolabels_details(self):
        infolabels = super().get_infolabels_details()
        return infolabels

    def get_infolabels_special(self, infolabels):
        try:
            infolabels['tvshowtitle'] = self.data[0]['title']
        except (TypeError, KeyError, IndexError):
            pass
        return infolabels

    def get_previous_season_episode_count(self, season):
        return sum(
            i['episode_count']
            for i in self.return_basemeta_db('season_episode_counts').cached_data
            if i['season'] < season
        )

    def get_aired_episodes(self):
        next_aired_id = self.get_data_value('next_aired_id')
        if not next_aired_id:
            if self.get_data_value('status') in ('Ended', 'Canceled'):
                return self.get_data_value('totalepisodes')
            return
        _, _, season, episode = next_aired_id.split('.')
        season, episode = try_int(season), try_int(episode)
        if is_unaired_timestamp(self.get_data_value('next_aired_premiered')):
            episode -= 1
        if season == 1:
            return episode
        if season > 1:
            return self.get_previous_season_episode_count(season) + episode

    def get_infoproperties_aired_episodes(self, infoproperties):
        if infoproperties.get('airedepisodes') is not None:
            return infoproperties
        aired_episodes = self.get_aired_episodes()
        if aired_episodes is not None:
            infoproperties['airedepisodes'] = aired_episodes
        return infoproperties

    def get_infoproperties_special(self, infoproperties):
        infoproperties = self.get_infoproperties_custom(infoproperties)
        infoproperties = self.get_infoproperties_translation(infoproperties)
        episode_groups = self.get_data_value('episode_groups')
        if episode_groups:
            infoproperties['episode_groups'] = episode_groups
        try:
            infoproperties['totalseasons'] = self.get_data_value('totalseasons')
            infoproperties['totalepisodes'] = self.get_data_value('totalepisodes')
        except (TypeError, KeyError, IndexError):
            pass
        infoproperties = self.get_infoproperties_ranks(infoproperties)
        infoproperties = self.get_infoproperties_next_ep(infoproperties)
        infoproperties = self.get_infoproperties_aired_episodes(infoproperties)
        return infoproperties
