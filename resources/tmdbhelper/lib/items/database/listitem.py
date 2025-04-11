from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.items.database.tmdbdata import ItemDetailsDataBaseCacheFactory


def configure_listitem(i):
    li = ListItem(**i)
    mediatype = li.infolabels.get('mediatype')

    if mediatype not in ('movie', 'tvshow', 'season', 'episode'):
        return li

    dbc = ItemDetailsDataBaseCacheFactory(mediatype)
    dbc.tmdb_id = li.unique_ids.get('tmdb')
    if mediatype in ['season', 'episode']:
        dbc.season = li.infolabels.get('season', 0)
        dbc.tmdb_id = li.unique_ids.get('tvshow.tmdb')
    if mediatype == 'episode':
        dbc.episode = li.infolabels.get('episode')

    with dbc.cache.get_database() as dbc.connection:
        if not dbc.data:
            return li
        li.set_details({'infolabels': dbc.data}, override=True)

    # li.art = self.get_item_artwork(item['artwork'], is_season=mediatype in ['season', 'episode'])
    return li
