from jurialmunkey.parser import try_int
from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.items.directories.tmdb.lists_view_db import ListSeries
from tmdbhelper.lib.items.directories.tmdb.lists_related import ListRecommendations
from tmdbhelper.lib.items.directories.tmdb.lists_seasons import ListFlatSeasons


class ListNextRecommendation(ContainerDirectory):
    def get_items(self, tmdb_type, tmdb_id, season=None, episode=None, **kwargs):
        if tmdb_type not in ('movie', 'tv'):
            return

        def _get_next_recommendation():
            items = ListRecommendations(-1, '').get_items(tmdb_id=tmdb_id, tmdb_type=tmdb_type)
            try:
                return items[0]
            except IndexError:
                return

        def _get_next_collection():
            collection_tmdb_id = self.get_collection_tmdb_id(tmdb_id=tmdb_id)
            items = ListSeries(-1, '').get_items(tmdb_id=collection_tmdb_id, tmdb_type='collection') or []
            items = sorted(items, key=lambda i: i['infolabels'].get('year') or 9999)
            try:
                iyear = next((i for i in items if try_int(i['unique_ids'].get('tmdb')) == try_int(tmdb_id)), None)
                iyear = iyear['infolabels']['year']
            except (KeyError, TypeError, AttributeError, IndexError):
                return
            if not iyear:
                return
            return next((i for i in items if try_int(i['infolabels'].get('year')) > try_int(iyear)), None)

        def _get_next_recommended_collection():
            return _get_next_collection() or _get_next_recommendation()

        def _get_next_episode(tmdb_id, season, episode):
            snum, enum = try_int(season), try_int(episode)
            if snum < 1 or enum < 0:
                return
            instance = ListFlatSeasons(-1, '')
            instance.hide_unaired = True
            for i in (instance.get_items(tmdb_id=tmdb_id) or []):
                i_snum = try_int(i['infolabels'].get('season', -1))
                if i_snum > snum:
                    return i
                if i_snum < snum:
                    continue
                i_enum = try_int(i['infolabels'].get('episode', -1))
                if i_enum > enum:
                    return i

        def _get_next_recommended_episode():
            item = None
            if season and episode:
                item = _get_next_episode(tmdb_id, season, episode)
            if not item:
                item = _get_next_recommendation()
                try:
                    item = _get_next_episode(item['infoproperties']['tmdb_id'], 1, 0)
                except (KeyError, TypeError):
                    return
            return item

        next_item = _get_next_recommended_episode() if tmdb_type == 'tv' else _get_next_recommended_collection()

        if not next_item:
            return

        self.kodi_db = self.get_kodi_database(tmdb_type)
        self.container_content = 'episodes' if tmdb_type == 'tv' else 'movies'
        return [next_item]
