# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html


def test_func(test_func, dialog_output=False, **kwargs):

    from timeit import default_timer as timer
    start_time = timer()

    def finalise(head='', data='', affix=''):
        total_time = timer() - start_time
        import xbmcgui
        from tmdbhelper.lib.files.futils import dumps_to_file
        xbmcgui.Dialog().textviewer(f'{head}', f'{data if dialog_output else bool(data)}')
        dump_data = {
            'func': test_func,
            'kwgs': kwargs,
            'time': f'{total_time:.3f} sec',
            'data': data,
        },
        dump_name = f'test_func_{test_func}{affix}.json'
        dumps_to_file(dump_data, 'log_data', dump_name, join_addon_data=True)

    def test_func_response(path, **kwargs):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        head = path
        data = TMDb().get_response_json(path, **kwargs)
        return finalise(head, data)

    def test_func_tmdbuser_response(path, **kwargs):
        from tmdbhelper.lib.api.tmdb.users import TMDbUser
        head = path
        data = TMDbUser().get_authorised_response_json(path, **kwargs)
        return finalise(head, data)

    def test_func_trakt_response(path, **kwargs):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        head = path
        data = TraktAPI().get_response(path, **kwargs)
        data = {'headers': dict(data.headers), 'request': data.json()}
        return finalise(head, data)

    def test_func_trakt_auth(**kwargs):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        tapi = TraktAPI()
        head = ''
        data = {'authorization': tapi.authenticator.authorization}
        return finalise(head, data)

    def test_func_mdblist_response(path, **kwargs):
        from tmdbhelper.lib.api.mdblist.api import MDbList
        head = path
        data = MDbList().get_response(path, **kwargs)
        data = {'headers': dict(data.headers), 'request': data.json()}
        return finalise(head, data)

    def test_func_fanarttv(ftv_type, ftv_id, **kwargs):
        from tmdbhelper.lib.api.fanarttv.api import FanartTV
        data = FanartTV().get_request(
            ftv_type, ftv_id,
            cache_force=7,  # Force dummy request caching to prevent rerequesting 404s
            cache_fallback={'dummy': None},
            cache_days=30)
        head = f'{ftv_type} {ftv_id}'
        return finalise(head, data)

    def test_func_baseitem_factory(mediatype, tmdb_id, season=None, episode=None, cache_refresh=None, del_database_init=False, attr='data'):
        from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
        sync = BaseItemFactory(mediatype)
        sync.tmdb_id = int(tmdb_id)
        sync.season = int(season) if season is not None else None
        sync.episode = int(episode) if episode is not None else None
        sync.cache_refresh = cache_refresh
        sync.cache.del_database_init() if del_database_init else None
        data = getattr(sync, attr)
        head = f'{mediatype} {tmdb_id} {season} {episode}'
        return finalise(head, data)

    def test_func_baseview_factory(import_attr, tmdb_type, tmdb_id, season=None, episode=None, filters=None, limit=None):
        from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
        sync = BaseViewFactory(import_attr, tmdb_type, int(tmdb_id), season, episode, filters, limit)
        data = sync.data
        head = f'{(import_attr, tmdb_type, int(tmdb_id))}'
        return finalise(head, data)

    def test_func_query_database(import_attr, **kwargs):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        query_database = FindQueriesDatabase()
        data = getattr(query_database, import_attr)(**kwargs)
        head = import_attr
        return finalise(head, data)

    def test_func_get_next_episodes(tmdb_id, season, episode, player=None, **kwargs):
        import xbmcgui
        from tmdbhelper.lib.player.details.details import get_next_episodes
        data = get_next_episodes(tmdb_id, season, episode, player)
        head = f'{(tmdb_id, season, episode)}'
        xbmcgui.Dialog().select(head, data, useDetails=True)

    def test_func_sync_next_episodes(import_attr, **kwargs):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        from tmdbhelper.lib.api.trakt.sync.datatype import SyncNextEpisodes
        sync = SyncNextEpisodes(TraktAPI().trakt_syncdata, 'show')
        func = getattr(sync, import_attr)
        head = import_attr
        data = func(**kwargs)
        return finalise(head, data, affix=import_attr)

    def test_func_get_response_sync(path, **kwargs):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        trakt_api = TraktAPI()
        path = trakt_api.get_request_url(path, **kwargs)
        data = trakt_api.get_api_request(path, headers=trakt_api.headers)
        data = data.json()
        head = path
        return finalise(head, data)

    def test_func_write_user_art(aspect, icon, parent_id, **kwargs):
        from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
        iddb = ItemDetailsDatabase()
        iddb.set_list_values(
            table='user_art',
            keys=('type', 'icon', 'parent_id'),
            values=(aspect, icon, parent_id),
            overwrite=True
        )

    def test_func_jrpc(dbid, **kwargs):
        from tmdbhelper.lib.api.kodi.rpc import get_jsonrpc
        method = "VideoLibrary.GetMovieDetails"
        properties = ["streamdetails"]
        params = {
            "movieid": int(dbid),
            "properties": properties}
        data = get_jsonrpc(method, params)
        head = dbid
        return finalise(head, data)

    def test_func_jrpc_directory(path, **kwargs):
        from tmdbhelper.lib.api.kodi.rpc import get_directory
        data = get_directory(path)
        head = path
        return finalise(head, data)

    routes = {
        'response': test_func_response,
        'trakt_response': test_func_trakt_response,
        'tmdbuser_response': test_func_tmdbuser_response,
        'mdblist_response': test_func_mdblist_response,
        'baseitem_factory': test_func_baseitem_factory,
        'baseview_factory': test_func_baseview_factory,
        'query_database': test_func_query_database,
        'fanarttv': test_func_fanarttv,
        'get_next_episodes': test_func_get_next_episodes,
        'sync_next_episodes': test_func_sync_next_episodes,
        'get_response_sync': test_func_get_response_sync,
        'write_user_art': test_func_write_user_art,
        'jrpc': test_func_jrpc,
        'jrpc_directory': test_func_jrpc_directory,
        'trakt_auth': test_func_trakt_auth,
    }

    return routes[test_func](**kwargs)
