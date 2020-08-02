import sys
import xbmc
import xbmcaddon
import xbmcgui
from resources.lib.plugin import Plugin
from resources.lib.traktapi import TraktAPI
from resources.lib.kodilibrary import KodiLibrary
import resources.lib.utils as utils
import resources.lib.libraryupdate as libraryupdate
_addon = xbmcaddon.Addon('plugin.video.themoviedb.helper')
_plugin = Plugin()


def browse():
    tmdb_id = sys.listitem.getProperty('tvshow.tmdb_id')
    path = 'plugin://plugin.video.themoviedb.helper/'
    path = path + '?info=seasons&type=tv&nextpage=True&tmdb_id={}'.format(tmdb_id)
    path = path + '&fanarttv=True' if _addon.getSettingBool('fanarttv_lookup') else path
    command = 'Container.Update({})' if xbmc.getCondVisibility("Window.IsMedia") else 'ActivateWindow(videos,{},return)'
    xbmc.executebuiltin(command.format(path))


def play():
    with utils.busy_dialog():
        suffix = 'force_dialog=True'
        tmdb_id, season, episode = None, None, None
        dbtype = sys.listitem.getVideoInfoTag().getMediaType()

        if dbtype == 'episode':
            tmdb_id = sys.listitem.getProperty('tvshow.tmdb_id')
            season = sys.listitem.getVideoInfoTag().getSeason()
            episode = sys.listitem.getVideoInfoTag().getEpisode()
            suffix += ',season={},episode={}'.format(season, episode)

        elif dbtype == 'movie':
            tmdb_id = sys.listitem.getProperty('tmdb_id') or sys.listitem.getUniqueID('tmdb')

        # Try to lookup ID if we don't have it
        if not tmdb_id and dbtype == 'episode':
            id_details = TraktAPI().get_item_idlookup(
                'episode', parent=True, tvdb_id=sys.listitem.getUniqueID('tvdb'),
                tmdb_id=sys.listitem.getUniqueID('tmdb'), imdb_id=sys.listitem.getUniqueID('imdb'))
            tmdb_id = id_details.get('show', {}).get('ids', {}).get('tmdb')

        elif not tmdb_id and dbtype == 'movie':
            tmdb_id = Plugin().get_tmdb_id(
                itemtype='movie', imdb_id=sys.listitem.getUniqueID('imdb'),
                query=sys.listitem.getVideoInfoTag().getTitle(), year=sys.listitem.getVideoInfoTag().getYear())

        if not tmdb_id or not dbtype:
            return xbmcgui.Dialog().ok('TheMovieDb Helper', _addon.getLocalizedString(32157))

        xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,play={},tmdb_id={},{})'.format(dbtype, tmdb_id, suffix))


def library():
    with utils.busy_dialog():
        title = utils.validify_filename(sys.listitem.getVideoInfoTag().getTitle())
        dbtype = sys.listitem.getVideoInfoTag().getMediaType()
        basedir_movie = _addon.getSettingString('movies_library') or 'special://profile/addon_data/plugin.video.themoviedb.helper/movies/'
        basedir_tv = _addon.getSettingString('tvshows_library') or 'special://profile/addon_data/plugin.video.themoviedb.helper/tvshows/'
        auto_update = _addon.getSettingBool('auto_update')

        # Setup our folders and file names
        if dbtype == 'movie':
            folder = '{} ({})'.format(title, sys.listitem.getVideoInfoTag().getYear())
            movie_name = '{} ({})'.format(title, sys.listitem.getVideoInfoTag().getYear())
            libraryupdate.create_file(movie_name, sys.listitem.getPath(), folder, basedir=basedir_movie)
            libraryupdate.create_nfo('movie', sys.listitem.getProperty('tmdb_id'), folder, basedir=basedir_movie)
            xbmc.executebuiltin('UpdateLibrary(video)') if auto_update else None

        elif dbtype == 'episode':
            folder = sys.listitem.getVideoInfoTag().getTVShowTitle()
            season_name = 'Season {}'.format(sys.listitem.getVideoInfoTag().getSeason())
            episode_name = 'S{:02d}E{:02d} - {}'.format(
                utils.try_parse_int(sys.listitem.getVideoInfoTag().getSeason()),
                utils.try_parse_int(sys.listitem.getVideoInfoTag().getEpisode()),
                title)
            libraryupdate.create_file(episode_name, sys.listitem.getPath(), folder, season_name, basedir=basedir_tv)
            libraryupdate.create_nfo('tv', sys.listitem.getProperty('tvshow.tmdb_id'), folder, basedir=basedir_tv)
            xbmc.executebuiltin('UpdateLibrary(video)') if auto_update else None

        elif dbtype == 'tvshow':
            folder = sys.listitem.getVideoInfoTag().getTVShowTitle() or title
            libraryupdate.add_tvshow(
                basedir=basedir_tv, folder=folder, url=sys.listitem.getPath(),
                tmdb_id=sys.listitem.getProperty('tmdb_id'), force=True)  # If we manually add a show force add it
            xbmc.executebuiltin('UpdateLibrary(video)') if auto_update else None

        elif dbtype == 'season':
            folder = sys.listitem.getVideoInfoTag().getTVShowTitle()
            episodes = KodiLibrary().get_directory(sys.listitem.getPath())
            season_name = 'Season {}'.format(sys.listitem.getVideoInfoTag().getSeason())
            for episode in episodes:
                if not episode.get('episode'):
                    continue  # Skip special episodes E00
                episode_path = libraryupdate.clean_content(episode.get('file'))
                episode_name = 'S{:02d}E{:02d} - {}'.format(
                    utils.try_parse_int(episode.get('season')),
                    utils.try_parse_int(episode.get('episode')),
                    utils.validify_filename(episode.get('title')))
                libraryupdate.create_file(episode_name, episode_path, folder, season_name, basedir=basedir_tv)
            libraryupdate.create_nfo('tv', sys.listitem.getProperty('tvshow.tmdb_id'), folder, basedir=basedir_tv)
            xbmc.executebuiltin('UpdateLibrary(video)') if auto_update else None

        else:
            return


def sync_userlist(remove_item=False):
    dbtype = sys.listitem.getVideoInfoTag().getMediaType()
    user_list = sys.listitem.getProperty('container.list_slug') if remove_item else None
    tmdb_id = sys.listitem.getProperty('tvshow.tmdb_id')
    imdb_id = sys.listitem.getUniqueID('imdb')
    tvdb_id = None
    if not dbtype == 'episode':
        tmdb_id = sys.listitem.getProperty('tmdb_id') or sys.listitem.getUniqueID('tmdb')
        tvdb_id = sys.listitem.getUniqueID('tvdb')
    if dbtype == 'movie':
        item_type = 'movie'
    elif dbtype in ['tvshow', 'season', 'episode']:
        item_type = 'show'
    else:  # Not the right type of item so lets exit
        return
    TraktAPI().sync_userlist(item_type, tmdb_id=tmdb_id, tvdb_id=tvdb_id, imdb_id=imdb_id, remove_item=remove_item, user_list=user_list)
    xbmc.executebuiltin('Container.Refresh')


def refresh_item():
    dbtype = sys.listitem.getVideoInfoTag().getMediaType()
    if dbtype == 'episode':
        d_args = (
            'tv', sys.listitem.getProperty('tvshow.tmdb_id'),
            sys.listitem.getVideoInfoTag().getSeason(),
            sys.listitem.getVideoInfoTag().getEpisode())
    elif dbtype == 'tvshow':
        d_args = ('tv', sys.listitem.getProperty('tmdb_id'))
    elif dbtype == 'movie':
        d_args = ('movie', sys.listitem.getProperty('tmdb_id'))
    else:
        return
    details = _plugin.tmdb.get_detailed_item(*d_args, cache_refresh=True)
    if details:
        xbmcgui.Dialog().ok(_addon.getLocalizedString(32144), _addon.getLocalizedString(32143).format(details.get('label')))
    xbmc.executebuiltin('Container.Refresh')


def action(action, tmdb_id=None, tmdb_type=None, season=None, episode=None, label=None):
    _traktapi = TraktAPI()

    if action == 'history':
        func = _traktapi.sync_history
    elif action == 'collection':
        func = _traktapi.sync_collection
    elif action == 'watchlist':
        func = _traktapi.sync_watchlist
    elif action == 'add_to_userlist':
        return sync_userlist()
    elif action == 'remove_from_userlist':
        return sync_userlist(remove_item=True)
    elif action == 'library_userlist':
        return libraryupdate.add_userlist(force=True)
    elif action == 'library':
        return library()
    elif action == 'refresh_item':
        return refresh_item()
    elif action == 'play':
        return play()
    elif action == 'open':
        return browse()
    else:
        return

    with utils.busy_dialog():
        if tmdb_id and tmdb_type:  # Passed details via script
            dbtype = utils.type_convert(tmdb_type, 'dbtype')
            label = label or 'this {}'.format(utils.type_convert(tmdb_type, 'trakt'))
            parent_tmdb_id = tmdb_id
        else:  # Context menu so retrieve details from listitem
            label = sys.listitem.getLabel()
            dbtype = sys.listitem.getVideoInfoTag().getMediaType()
            tmdb_id = sys.listitem.getProperty('tmdb_id')
            parent_tmdb_id = sys.listitem.getProperty('tvshow.tmdb_id') if dbtype == 'episode' else tmdb_id
            season = sys.listitem.getVideoInfoTag().getSeason() if dbtype == 'episode' else None
            episode = sys.listitem.getVideoInfoTag().getEpisode() if dbtype == 'episode' else None

        if tmdb_type == 'episode':  # Passed episode details via script
            if not season or not episode:  # Need season and episode for episodes
                return  # Need season and episode if run from script so leave
            # Retrieve episode details so that we can get tmdb_id for episode
            episode_details = _plugin.tmdb.get_detailed_item(tmdb_type, parent_tmdb_id, season=season, episode=episode)
            tmdb_id = episode_details.get('infoproperties', {}).get('imdb_id')

        if dbtype == 'movie':
            tmdb_type = 'movie'
        elif dbtype == 'tvshow':
            tmdb_type = 'tv'
        elif dbtype == 'episode':
            tmdb_type = 'episode'
        else:
            return

        # Check if we're adding or removing the item and confirm with the user that they want to do that
        trakt_ids = func(utils.type_convert(tmdb_type, 'trakt'), 'tmdb', cache_refresh=True)
        boolean = 'remove' if int(tmdb_id) in trakt_ids else 'add'
        dialog_header = 'Trakt {0}'.format(action.capitalize())
        dialog_text = xbmcaddon.Addon().getLocalizedString(32065) if boolean == 'add' else xbmcaddon.Addon().getLocalizedString(32064)
        dialog_text = dialog_text.format(utils.try_decode_string(label), action.capitalize(), tmdb_type, tmdb_id)
        dialog_text = dialog_text + ' Season: {}  Episode: {}'.format(season, episode) if dbtype == 'episode' else dialog_text
        if not xbmcgui.Dialog().yesno(dialog_header, dialog_text):
            return

        with utils.busy_dialog():
            slug_type = 'show' if tmdb_type == 'episode' else utils.type_convert(tmdb_type, 'trakt')
            trakt_type = utils.type_convert(tmdb_type, 'trakt')
            slug = _traktapi.get_traktslug(slug_type, 'tmdb', parent_tmdb_id)
            item = _traktapi.get_details(slug_type, slug, season=season, episode=episode)
            items = {trakt_type + 's': [item]}
            func(slug_type, mode=boolean, items=items)

        dialog_header = 'Trakt {0}'.format(action.capitalize())
        dialog_text = xbmcaddon.Addon().getLocalizedString(32062) if boolean == 'add' else xbmcaddon.Addon().getLocalizedString(32063)
        dialog_text = dialog_text.format(tmdb_id, action.capitalize())
        xbmcgui.Dialog().ok(dialog_header, dialog_text)
        xbmc.executebuiltin('Container.Refresh')
