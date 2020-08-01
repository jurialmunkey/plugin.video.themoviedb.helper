import sys
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import datetime
import simplecache
from resources.lib.plugin import Plugin
from resources.lib.traktapi import TraktAPI
from resources.lib.kodilibrary import KodiLibrary
from resources.lib.constants import LIBRARY_ADD_LIMIT_TVSHOWS, LIBRARY_ADD_LIMIT_MOVIES
import resources.lib.utils as utils
_addon = xbmcaddon.Addon('plugin.video.themoviedb.helper')
_plugin = Plugin()
_debuglogging = _addon.getSettingBool('debug_logging')


def library_cleancontent_replacer(content, old, new):
    content = content.replace(old, new)
    return library_cleancontent_replacer(content, old, new) if old in content else content


def library_cleancontent(content, details='info=play'):
    content = content.replace('info=flatseasons', details)
    content = content.replace('info=details', details)
    content = content.replace('fanarttv=True', '')
    content = content.replace('widget=True', '')
    content = content.replace('localdb=True', '')
    content = content.replace('nextpage=True', '')
    content = library_cleancontent_replacer(content, '&amp;', '&')
    content = library_cleancontent_replacer(content, '&&', '&')
    content = library_cleancontent_replacer(content, '?&', '?')
    content = content + '&islocal=True' if '&islocal=True' not in content else content
    return content


def library_createpath(path):
    if xbmcvfs.exists(path):
        return path
    if xbmcvfs.mkdirs(path):
        utils.kodi_log(u'ADD LIBRARY -- Created path:\n{}'.format(path), 2)
        return path
    if _addon.getSettingBool('ignore_folderchecking'):
        utils.kodi_log(u'ADD LIBRARY -- xbmcvfs reports folder does NOT exist:\n{}\nIGNORING ERROR: User set folder checking to ignore'.format(path), 2)
        return path


def library_createfile(filename, content, *args, **kwargs):
    """
    Create the file and folder structure: filename=.strm file, content= content of file.
    *args = folders to create.
    """
    path = kwargs.get('basedir', '').replace('\\', '/')  # Convert MS-DOS style paths to UNIX style

    if not path:
        utils.kodi_log(u'ADD LIBRARY -- No basedir specified!', 2)
        return
    for folder in args:
        folder = utils.validify_filename(folder)
        path = '{}{}/'.format(path, folder)

    content = library_cleancontent(content) if kwargs.get('clean_url', True) else content

    if not content:
        utils.kodi_log(u'ADD LIBRARY -- No content specified!', 2)
        return
    if not filename:
        utils.kodi_log(u'ADD LIBRARY -- No filename specified!', 2)
        return

    if not library_createpath(path):
        xbmcgui.Dialog().ok(
            xbmc.getLocalizedString(20444),
            _addon.getLocalizedString(32122) + ' [B]{}[/B]'.format(path),
            _addon.getLocalizedString(32123))
        utils.kodi_log(u'ADD LIBRARY -- XBMCVFS unable to create path:\n{}'.format(path), 2)
        return

    filepath = '{}{}.{}'.format(path, utils.validify_filename(filename), kwargs.get('file_ext', 'strm'))
    f = xbmcvfs.File(filepath, 'w')
    f.write(utils.try_encode_string(content))
    f.close()

    utils.kodi_log(u'ADD LIBRARY -- Successfully added:\n{}\n{}'.format(filepath, content), 2)
    return filepath


def library_create_nfo(tmdbtype, tmdb_id, *args, **kwargs):
    filename = 'movie' if tmdbtype == 'movie' else 'tvshow'
    content = 'https://www.themoviedb.org/{}/{}'.format(tmdbtype, tmdb_id)
    library_createfile(filename, content, file_ext='nfo', *args, **kwargs)


def library_addtvshow(basedir=None, folder=None, url=None, tmdb_id=None, tvdb_id=None, imdb_id=None, p_dialog=None, cache=None, force=False):
    if not basedir or not folder or not url or not tmdb_id:
        return

    # Get our cached info
    if not cache:
        cache = simplecache.SimpleCache()
    cache_name = 'plugin.video.themoviedb.helper.library_autoupdate_tv.{}'.format(tmdb_id)
    cache_info = {} if force else cache.get(cache_name) or {}
    cache_version = 5

    # If there's already a folder for a different show with the same name then create a separate folder
    nfo_id = utils.get_tmdbid_nfo(basedir, folder) if folder in xbmcvfs.listdir(basedir)[0] else None
    if nfo_id and utils.try_parse_int(nfo_id) != utils.try_parse_int(tmdb_id):
        folder += ' (TMDB {})'.format(tmdb_id)

    # Only use cache info if version matches
    if not cache_info.get('version') or cache_info.get('version') != cache_version:
        cache_info = {}

    # If there is a next check value and it hasn't elapsed then skip the update
    next_check = cache_info.get(tmdb_id, {}).get('next_check')
    if next_check and utils.convert_timestamp(next_check, "%Y-%m-%d", 10) > datetime.datetime.today():
        if _debuglogging:
            log_msg = cache_info.get(tmdb_id, {}).get('log_msg') or ''
            utils.kodi_log(u'Skipping updating {} (TMDB {})\nNext update {}{}'.format(
                cache_info.get(tmdb_id, {}).get('name'), tmdb_id, next_check, log_msg), 2)
        return

    # Get all seasons in the tvshow except specials
    details_tvshow = _plugin.tmdb.get_request_sc('tv', tmdb_id)
    if not details_tvshow:
        return

    # Create the .nfo file in the folder
    library_create_nfo('tv', tmdb_id, folder, basedir=basedir)

    # Construct our cache object
    today_date = datetime.datetime.today().strftime('%Y-%m-%d')
    my_history = {
        'version': cache_version,
        'name': details_tvshow.get('name', ''),
        'skipped': [],
        'episodes': [],
        'latest_season': 0,
        'next_check': today_date,
        'last_check': today_date,
        'log_msg': ''}

    # Set the next check date for this show
    next_aired = details_tvshow.get('next_episode_to_air', {})
    if next_aired and next_aired.get('air_date'):
        next_aired_dt = utils.convert_timestamp(next_aired.get('air_date'), "%Y-%m-%d", 10)
        if next_aired_dt > datetime.datetime.today():
            if next_aired_dt < (datetime.datetime.today() + datetime.timedelta(days=7)):
                my_history['next_check'] = next_aired.get('air_date')
                my_history['log_msg'] = '\nShow had next aired date this week'
                # Check again on the next aired date
            elif next_aired_dt < (datetime.datetime.today() + datetime.timedelta(days=30)):
                my_next_check = datetime.datetime.today() + datetime.timedelta(days=7)
                my_history['next_check'] = my_next_check.strftime('%Y-%m-%d')
                my_history['log_msg'] = '\nShow has next aired date this month'
                # Check again in a week just to be safe in case air date changes
            else:
                my_next_check = datetime.datetime.today() + datetime.timedelta(days=30)
                my_history['next_check'] = my_next_check.strftime('%Y-%m-%d')
                my_history['log_msg'] = '\nShow has next aired date in more than a month'
                # Check again in a month just to be safe in case air date changes
        else:
            next_aired = None  # Next aired was in the past for some reason so dont use that date

    last_aired = details_tvshow.get('last_episode_to_air', {})
    if not next_aired and last_aired and last_aired.get('air_date'):
        last_aired_dt = utils.convert_timestamp(last_aired.get('air_date'), "%Y-%m-%d", 10)
        if last_aired_dt > (datetime.datetime.today() - datetime.timedelta(days=30)):
            my_next_check = datetime.datetime.today() + datetime.timedelta(days=1)
            my_history['next_check'] = my_next_check.strftime('%Y-%m-%d')
            my_history['log_msg'] = '\nShow aired in last month but no next aired date'
            # Show might be currently airing but just hasnt updated next date yet so check again tomorrow
        elif last_aired_dt > (datetime.datetime.today() - datetime.timedelta(days=90)):
            my_history['log_msg'] = '\nShow aired in last quarter but not in last month'
            my_next_check = datetime.datetime.today() + datetime.timedelta(days=7)
            my_history['next_check'] = my_next_check.strftime('%Y-%m-%d')
            # Show might be on a mid-season break so check again in a week for a return date
        elif details_tvshow.get('status') in ['Canceled', 'Ended']:
            my_history['log_msg'] = '\nShow was canceled or ended'
            my_next_check = datetime.datetime.today() + datetime.timedelta(days=30)
            my_history['next_check'] = my_next_check.strftime('%Y-%m-%d')
            # Show was canceled so check again in a month just to be safe
        else:
            my_history['log_msg'] = '\nShow last aired more than 3 months ago and no next aired date set'
            my_next_check = datetime.datetime.today() + datetime.timedelta(days=7)
            my_history['next_check'] = my_next_check.strftime('%Y-%m-%d')
            # Show hasnt aired in a while so check every week for a return date

    prev_added_eps = cache_info.get(tmdb_id, {}).get('episodes') or []
    prev_skipped_eps = cache_info.get(tmdb_id, {}).get('skipped') or []

    seasons = details_tvshow.get('seasons', [])
    s_total = len(seasons)
    for s_count, season in enumerate(seasons):
        # Skip special seasons
        if season.get('season_number', 0) == 0:
            if _debuglogging:
                utils.kodi_log(u'{} (TMDB {})\nSpecial Season. Skipping...'.format(details_tvshow.get('name'), tmdb_id), 2)
            s_total -= 1
            continue

        season_name = u'Season {}'.format(season.get('season_number'))

        # Update our progress dialog
        if p_dialog:
            p_dialog_val = ((s_count + 1) * 100) // s_total
            p_dialog_msg = u'{} {} - {}...'.format(_addon.getLocalizedString(32167), details_tvshow.get('original_name'), season_name)
            p_dialog.update(p_dialog_val, message=p_dialog_msg)

        # If weve scanned before we only want to scan the most recent seasons (that have already started airing)
        latest_season = utils.try_parse_int(cache_info.get('latest_season', 0))
        if utils.try_parse_int(season.get('season_number', 0)) < latest_season:
            if _debuglogging:
                utils.kodi_log(u'{} (TMDB {})\nPreviously Added {}. Skipping...'.format(details_tvshow.get('name'), tmdb_id, season_name), 2)
            continue

        # Get all episodes in the season except specials
        details_season = _plugin.tmdb.get_request_sc('tv', tmdb_id, 'season', season.get('season_number'))
        if not details_season:
            utils.kodi_log(u'{} (TMDB {})\nNo details found for {}. Skipping...'.format(details_tvshow.get('name'), tmdb_id, season_name))
            return
        episodes = [i for i in details_season.get('episodes', []) if i.get('episode_number', 0) != 0]  # Only get non-special seasons
        skipped_eps, future_eps, library_eps = [], [], []
        for e_count, episode in enumerate(episodes):
            episode_name = 'S{:02d}E{:02d} - {}'.format(
                utils.try_parse_int(season.get('season_number')), utils.try_parse_int(episode.get('episode_number')),
                utils.validify_filename(episode.get('name')))

            my_history['episodes'].append(episode_name)

            # Skip episodes we added in the past
            if episode_name in prev_added_eps:
                if episode_name not in prev_skipped_eps:
                    if _debuglogging:
                        skipped_eps.append(episode_name)
                    continue

            # Skip future episodes
            if _addon.getSettingBool('hide_unaired_episodes'):
                air_date = utils.convert_timestamp(episode.get('air_date'), "%Y-%m-%d", 10)
                if not air_date or air_date > datetime.datetime.now():
                    if _debuglogging:
                        future_eps.append(episode_name)
                    my_history['skipped'].append(episode_name)
                    continue

            # Check if item has already been added
            if _plugin.get_db_info(info='dbid', tmdbtype='episode', imdb_id=imdb_id, tmdb_id=tmdb_id, season=season.get('season_number'), episode=episode.get('episode_number')):
                if _debuglogging:
                    library_eps.append(episode_name)
                continue

            # Update progress dialog
            if p_dialog:
                p_dialog.update(((e_count + 1) * 100) // len(episodes))

            # Create our .strm file for the episode
            episode_path = 'plugin://plugin.video.themoviedb.helper/?info=play&type=episode&islocal=True'
            episode_path += '&tmdb_id={}&season={}&episode={}'.format(tmdb_id, season, episode.get('episode_number'))
            library_createfile(episode_name, episode_path, folder, season_name, basedir=basedir)

        # Some logging of what we did
        if _debuglogging:
            klog_msg = u'{} (TMDB {}) - {} - Done!'.format(details_tvshow.get('name'), tmdb_id, season_name)
            if skipped_eps:
                klog_msg += u'\nSkipped Previously Added Episodes:\n{}'.format(skipped_eps)
            if library_eps:
                klog_msg += u'\nSkipped Episodes in Library:\n{}'.format(library_eps)
            if future_eps:
                klog_msg += u'\nSkipped Unaired Episodes:\n{}'.format(future_eps)
            utils.kodi_log(klog_msg, 2)

        # Store a season value of where we got up to
        if len(episodes) > 2:
            air_date = utils.convert_timestamp(season.get('air_date'), "%Y-%m-%d", 10)
            if air_date and air_date < datetime.datetime.now():  # Make sure the season has actually aired!
                my_history['latest_season'] = utils.try_parse_int(season.get('season_number'))

    # Store details about what we did into the cache
    cache.set(cache_name, my_history, expiration=datetime.timedelta(days=120))


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


def library_userlist(user_slug=None, list_slug=None, confirmation_dialog=True, allow_update=True, busy_dialog=True, force=False):
    user_slug = user_slug or sys.listitem.getProperty('Item.user_slug')
    list_slug = list_slug or sys.listitem.getProperty('Item.list_slug')

    if busy_dialog:
        with utils.busy_dialog():
            request = TraktAPI().get_response_json('users', user_slug, 'lists', list_slug, 'items')
    else:
        request = TraktAPI().get_response_json('users', user_slug, 'lists', list_slug, 'items')

    if not request:
        return

    i_count = 0
    i_total = len(request)

    if confirmation_dialog:
        d_head = _addon.getLocalizedString(32125)
        d_body = _addon.getLocalizedString(32126)
        d_body += '\n[B]{}[/B] {} [B]{}[/B]'.format(list_slug, _addon.getLocalizedString(32127), user_slug)
        d_body += '\n\n[B][COLOR=red]{}[/COLOR][/B] '.format(xbmc.getLocalizedString(14117)) if i_total > 20 else '\n\n'
        d_body += '{} [B]{}[/B] {}.'.format(_addon.getLocalizedString(32128), i_total, _addon.getLocalizedString(32129))
        if not xbmcgui.Dialog().yesno(d_head, d_body):
            return

    """
    IMPORTANT: Do not change limits.
    Please respect the APIs that provide this data for free.
    """
    if i_total > LIBRARY_ADD_LIMIT_TVSHOWS:
        i_total_shows = 0
        i_total_films = 0
        for i in request:
            if i.get('type') == 'show':
                i_total_shows += 1
            elif i.get('type') == 'movie':
                i_total_films += 1
        if i_total_shows > LIBRARY_ADD_LIMIT_TVSHOWS or i_total_films > LIBRARY_ADD_LIMIT_MOVIES:
            xbmcgui.Dialog().notification('TMDbHelper', _addon.getLocalizedString(32165))
            if confirmation_dialog:
                d_head = _addon.getLocalizedString(32125)
                d_body = '[B]{}[/B] {} [B]{}[/B]'.format(list_slug, _addon.getLocalizedString(32127), user_slug)
                d_body += '\n\n[B][COLOR=red]{}[/COLOR][/B] '.format(xbmc.getLocalizedString(14117))
                d_body += _addon.getLocalizedString(32128)
                if i_total_shows > LIBRARY_ADD_LIMIT_TVSHOWS:
                    d_body += ' [B]{}[/B] {}'.format(i_total_shows, xbmc.getLocalizedString(20343))
                if i_total_films > LIBRARY_ADD_LIMIT_MOVIES:
                    d_body += ' [B]{}[/B] {}'.format(i_total_films, xbmc.getLocalizedString(20342))
                d_body += _addon.getLocalizedString(32164).format(LIBRARY_ADD_LIMIT_TVSHOWS, LIBRARY_ADD_LIMIT_MOVIES)
                xbmcgui.Dialog().ok(d_head, d_body)
            return

    p_dialog = xbmcgui.DialogProgressBG() if busy_dialog else None
    p_dialog.create('TMDbHelper', _addon.getLocalizedString(32166)) if p_dialog else None
    basedir_movie = _addon.getSettingString('movies_library') or 'special://profile/addon_data/plugin.video.themoviedb.helper/movies/'
    basedir_tv = _addon.getSettingString('tvshows_library') or 'special://profile/addon_data/plugin.video.themoviedb.helper/tvshows/'
    all_movies = []
    all_tvshows = []

    # Create the cache object now so that library addtvshow method doesnt need to constantly init it
    cache = simplecache.SimpleCache()

    for i in request:
        i_count += 1
        i_type = i.get('type')
        if i_type not in ['movie', 'show']:
            continue  # Only get movies or tvshows

        item = i.get(i_type, {})
        tmdb_id = item.get('ids', {}).get('tmdb')
        imdb_id = item.get('ids', {}).get('imdb')
        tvdb_id = item.get('ids', {}).get('tvdb')
        if not tmdb_id:
            continue  # Don't bother if there isn't a tmdb_id as lookup is too expensive for long lists

        if i_type == 'movie':  # Add any movies
            content = 'plugin://plugin.video.themoviedb.helper/?info=play&tmdb_id={}&type=movie'.format(tmdb_id)
            folder = u'{} ({})'.format(item.get('title'), item.get('year'))
            movie_name = u'{} ({})'.format(item.get('title'), item.get('year'))
            db_file = _plugin.get_db_info(info='file', tmdbtype='movie', imdb_id=imdb_id, tmdb_id=tmdb_id)
            if db_file:
                all_movies.append(('filename', db_file.replace('\\', '/').split('/')[-1]))
                p_dialog.update((i_count * 100) // i_total, message=u'Found {} in library. Skipping...'.format(movie_name)) if p_dialog else None
                utils.kodi_log(u'Trakt List Add to Library\nFound {} in library. Skipping...'.format(movie_name), 0)
                continue
            p_dialog.update((i_count * 100) // i_total, message=u'Adding {} to library...'.format(movie_name)) if p_dialog else None
            utils.kodi_log(u'Adding {} to library...'.format(movie_name), 0)
            db_file = library_createfile(movie_name, content, folder, basedir=basedir_movie)
            library_create_nfo('movie', tmdb_id, folder, basedir=basedir_movie)
            all_movies.append(('filename', db_file.split('/')[-1]))

        if i_type == 'show':  # Add whole tvshows
            all_tvshows.append(('title', item.get('title')))
            content = 'plugin://plugin.video.themoviedb.helper/?info=seasons&nextpage=True&tmdb_id={}&type=tv'.format(tmdb_id)
            folder = u'{}'.format(item.get('title'))
            p_dialog.update((i_count * 100) // i_total, message=u'Adding {} to library...'.format(item.get('title'))) if p_dialog else None
            library_addtvshow(basedir=basedir_tv, folder=folder, url=content, tmdb_id=tmdb_id, imdb_id=imdb_id, tvdb_id=tvdb_id, p_dialog=p_dialog, cache=cache, force=force)

    if p_dialog:
        p_dialog.close()
    if all_movies:
        create_playlist(all_movies, 'movies', user_slug, list_slug)
    if all_tvshows:
        create_playlist(all_tvshows, 'tvshows', user_slug, list_slug)
    if allow_update and _addon.getSettingBool('auto_update'):
        xbmc.executebuiltin('UpdateLibrary(video)')


def create_playlist(items, dbtype, user_slug, list_slug):
    """
    Creates a smart playlist from a list of titles
    """
    filename = '{}-{}-{}'.format(user_slug, list_slug, dbtype)
    filepath = 'special://profile/playlists/video/'
    fcontent = u'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
    fcontent += u'\n<smartplaylist type="{}">'.format(dbtype)
    fcontent += u'\n    <name>{} by {} ({})</name>'.format(list_slug, user_slug, dbtype)
    fcontent += u'\n    <match>any</match>'
    for i in items:
        fcontent += u'\n    <rule field="{}" operator="is"><value>{}</value></rule>'.format(i[0], i[1])
    fcontent += u'\n</smartplaylist>'
    library_createfile(filename, fcontent, basedir=filepath, file_ext='xsp', clean_url=False)


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
            library_createfile(movie_name, sys.listitem.getPath(), folder, basedir=basedir_movie)
            library_create_nfo('movie', sys.listitem.getProperty('tmdb_id'), folder, basedir=basedir_movie)
            xbmc.executebuiltin('UpdateLibrary(video)') if auto_update else None

        elif dbtype == 'episode':
            folder = sys.listitem.getVideoInfoTag().getTVShowTitle()
            season_name = 'Season {}'.format(sys.listitem.getVideoInfoTag().getSeason())
            episode_name = 'S{:02d}E{:02d} - {}'.format(
                utils.try_parse_int(sys.listitem.getVideoInfoTag().getSeason()),
                utils.try_parse_int(sys.listitem.getVideoInfoTag().getEpisode()),
                title)
            library_createfile(episode_name, sys.listitem.getPath(), folder, season_name, basedir=basedir_tv)
            library_create_nfo('tv', sys.listitem.getProperty('tvshow.tmdb_id'), folder, basedir=basedir_tv)
            xbmc.executebuiltin('UpdateLibrary(video)') if auto_update else None

        elif dbtype == 'tvshow':
            folder = sys.listitem.getVideoInfoTag().getTVShowTitle() or title
            library_addtvshow(
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
                episode_path = library_cleancontent(episode.get('file'))
                episode_name = 'S{:02d}E{:02d} - {}'.format(
                    utils.try_parse_int(episode.get('season')),
                    utils.try_parse_int(episode.get('episode')),
                    utils.validify_filename(episode.get('title')))
                library_createfile(episode_name, episode_path, folder, season_name, basedir=basedir_tv)
            library_create_nfo('tv', sys.listitem.getProperty('tvshow.tmdb_id'), folder, basedir=basedir_tv)
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
        return library_userlist(force=True)
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
