import sys
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
from resources.lib.traktapi import TraktAPI
from resources.lib.kodilibrary import KodiLibrary
import resources.lib.utils as utils


def library_cleancontent_replacer(content, old, new):
    content = content.replace(old, new)
    return library_cleancontent_replacer(content, old, new) if old in content else content


def library_cleancontent(content, details='info=play'):
    content = content.replace('info=details', details)
    content = content.replace('fanarttv=True', '')
    content = content.replace('widget=True', '')
    content = content.replace('localdb=True', '')
    content = content.replace('nextpage=True', '')
    content = library_cleancontent_replacer(content, '&amp;', '&')
    content = library_cleancontent_replacer(content, '&&', '&')
    content = library_cleancontent_replacer(content, '?&', '?')
    return content


def library_createfile(filename, content, *args, **kwargs):
    """
    Create the file and folder structure: filename=.strm file, content= content of file.
    *args = folders to create.
    """
    file_ext = kwargs.pop('file_ext', 'strm')
    path = 'special://profile/addon_data/plugin.video.themoviedb.helper'
    content = library_cleancontent(content)
    for folder in args:
        folder = utils.validify_filename(folder)
        path = '{}/{}'.format(path, folder) if path else folder
    if not path:
        return utils.kodi_log('ADD LIBRARY -- No path specified!', 1)
    if not content:
        return utils.kodi_log('ADD LIBRARY -- No content specified!', 1)
    if not filename:
        return utils.kodi_log('ADD LIBRARY -- No filename specified!', 1)
    if not xbmcvfs.exists(path) and not xbmcvfs.mkdirs(path):
        return utils.kodi_log('ADD LIBRARY -- Failed to create path:\n{}'.format(path), 1)
    filename = '{}.{}'.format(utils.validify_filename(filename), file_ext)
    filepath = '{}/{}'.format(path, filename)
    f = xbmcvfs.File(filepath, 'w')
    f.write(str(content))
    f.close()
    utils.kodi_log('ADD LIBRARY -- Successfully added:\n{}\n{}'.format(filepath, content), 1)


def library_create_nfo(tmdbtype, tmdb_id, *args):
    filename = 'movie' if tmdbtype == 'movie' else 'tvshow'
    content = 'https://www.themoviedb.org/{}/{}'.format(tmdbtype, tmdb_id)
    library_createfile(filename, content, file_ext='nfo', *args)


def library():
    with utils.busy_dialog():
        title = utils.validify_filename(sys.listitem.getVideoInfoTag().getTitle())
        dbtype = sys.listitem.getVideoInfoTag().getMediaType()
        basedir_movie = 'movies'
        basedir_tv = 'tvshows'

        # Setup our folders and file names
        if dbtype == 'movie':
            folder = '{} ({})'.format(title, sys.listitem.getVideoInfoTag().getYear())
            movie_name = '{} ({})'.format(title, sys.listitem.getVideoInfoTag().getYear())
            library_createfile(movie_name, sys.listitem.getPath(), basedir_movie, folder)
            library_create_nfo('movie', sys.listitem.getProperty('tmdb_id'), basedir_movie, folder)

        elif dbtype == 'episode':
            folder = sys.listitem.getVideoInfoTag().getTVShowTitle()
            season_name = 'Season {}'.format(sys.listitem.getVideoInfoTag().getSeason())
            episode_name = 'S{:02d}E{:02d} - {}'.format(
                utils.try_parse_int(sys.listitem.getVideoInfoTag().getSeason()),
                utils.try_parse_int(sys.listitem.getVideoInfoTag().getEpisode()),
                title)
            library_createfile(episode_name, sys.listitem.getPath(), basedir_tv, folder, season_name)

        elif dbtype == 'tvshow':
            folder = sys.listitem.getVideoInfoTag().getTVShowTitle() or title
            seasons = library_cleancontent(sys.listitem.getPath(), details='info=seasons')
            seasons = KodiLibrary().get_directory(seasons)
            library_create_nfo('tv', sys.listitem.getProperty('tmdb_id'), basedir_tv, folder)
            for season in seasons:
                if not season.get('season'):
                    continue  # Skip special seasons S00
                season_name = 'Season {}'.format(season.get('season'))
                episodes = KodiLibrary().get_directory(season.get('file'))
                for episode in episodes:
                    if not episode.get('episode'):
                        continue  # Skip special episodes E00
                    episode_path = library_cleancontent(episode.get('file'))
                    episode_name = 'S{:02d}E{:02d} - {}'.format(
                        utils.try_parse_int(episode.get('season')),
                        utils.try_parse_int(episode.get('episode')),
                        utils.validify_filename(episode.get('title')))
                    library_createfile(episode_name, episode_path, basedir_tv, folder, season_name)

        elif dbtype == 'season':
            folder = sys.listitem.getVideoInfoTag().getTVShowTitle()
            episodes = KodiLibrary().get_directory(sys.listitem.getPath())
            season_name = 'Season {}'.format(sys.listitem.getVideoInfoTag().getSeason())
            for episode in episodes:
                if not episode.get('episode'):
                    continue  # Skip special episodes E00
                episode_path = library_cleancontent(episode.get('file'))
                episode_name = 'S{:02d}E{:02d} - {}'.format(
                    utils.try_parse_int(episode.get('season')),
                    utils.try_parse_int(episode.get('episode')),
                    utils.validify_filename(episode.get('title')))
                library_createfile(episode_name, episode_path, basedir_tv, folder, season_name)

        else:
            return


def action(action):
    _traktapi = TraktAPI()

    if action == 'history':
        func = _traktapi.sync_history
    elif action == 'collection':
        func = _traktapi.sync_collection
    elif action == 'watchlist':
        func = _traktapi.sync_watchlist
    elif action == 'library':
        return library()
    else:
        return

    with utils.busy_dialog():
        label = sys.listitem.getLabel()
        dbtype = sys.listitem.getVideoInfoTag().getMediaType()
        tmdb_id = sys.listitem.getProperty('tmdb_id')
        tmdb_type = 'movie' if dbtype == 'movie' else 'tv'
        trakt_ids = func(utils.type_convert(tmdb_type, 'trakt'), 'tmdb')
        boolean = 'remove' if int(tmdb_id) in trakt_ids else 'add'

    dialog_header = 'Trakt {0}'.format(action.capitalize())
    dialog_text = xbmcaddon.Addon().getLocalizedString(32065) if boolean == 'add' else xbmcaddon.Addon().getLocalizedString(32064)
    dialog_text = dialog_text.format(label, action.capitalize(), dbtype.capitalize(), tmdb_id)
    if not xbmcgui.Dialog().yesno(dialog_header, dialog_text):
        return

    with utils.busy_dialog():
        trakt_type = utils.type_convert(dbtype, 'trakt')
        slug_type = 'show' if dbtype == 'episode' else trakt_type
        slug = _traktapi.get_traktslug(slug_type, 'tmdb', tmdb_id)
        season = sys.listitem.getVideoInfoTag().getSeason() if dbtype == 'episode' else None
        episode = sys.listitem.getVideoInfoTag().getEpisode() if dbtype == 'episode' else None
        item = _traktapi.get_details(slug_type, slug, season=season, episode=episode)
        items = {trakt_type + 's': [item]}
        func(slug_type, mode=boolean, items=items)

    dialog_header = 'Trakt {0}'.format(action.capitalize())
    dialog_text = xbmcaddon.Addon().getLocalizedString(32062) if boolean == 'add' else xbmcaddon.Addon().getLocalizedString(32063)
    dialog_text = dialog_text.format(tmdb_id, action.capitalize())
    xbmcgui.Dialog().ok(dialog_header, dialog_text)
    xbmc.executebuiltin('Container.Refresh')
