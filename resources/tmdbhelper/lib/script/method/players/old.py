# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html


def play_using(play_using, mode='play', **kwargs):
    from tmdbhelper.lib.addon.plugin import get_infolabel
    from tmdbhelper.lib.files.futils import read_file
    from jurialmunkey.parser import parse_paramstring

    def _update_from_listitem(dictionary):
        url = get_infolabel('ListItem.FileNameAndPath') or ''
        if url[-5:] == '.strm':
            url = read_file(url)
        params = {}
        if url.startswith('plugin://plugin.video.themoviedb.helper/?'):
            params = parse_paramstring(url.replace('plugin://plugin.video.themoviedb.helper/?', ''))
        if params.pop('info', None) == 'play':
            dictionary.update(params)
        if dictionary.get('tmdb_type'):
            return dictionary
        dbtype = get_infolabel('ListItem.DBType')
        if dbtype == 'movie':
            dictionary['tmdb_type'] = 'movie'
            dictionary['tmdb_id'] = get_infolabel('ListItem.UniqueId(tmdb)')
            dictionary['imdb_id'] = get_infolabel('ListItem.UniqueId(imdb)')
            dictionary['query'] = get_infolabel('ListItem.Title')
            dictionary['year'] = get_infolabel('ListItem.Year')
            if dictionary['tmdb_id'] or dictionary['imdb_id'] or dictionary['query']:
                return dictionary
        elif dbtype == 'episode':
            dictionary['tmdb_type'] = 'tv'
            dictionary['query'] = get_infolabel('ListItem.TVShowTitle')
            dictionary['ep_year'] = get_infolabel('ListItem.Year')
            dictionary['season'] = get_infolabel('ListItem.Season')
            dictionary['episode'] = get_infolabel('ListItem.Episode')
            if dictionary['query'] and dictionary['season'] and dictionary['episode']:
                return dictionary

    if 'tmdb_type' not in kwargs and not _update_from_listitem(kwargs):
        return
    kwargs['mode'] = mode
    kwargs['player'] = play_using
    from tmdbhelper.lib.player.method.play import play_external
    play_external(**kwargs)


def update_players():
    from xbmcgui import Dialog
    from tmdbhelper.lib.files.downloader import Downloader
    from tmdbhelper.lib.addon.plugin import set_setting
    from tmdbhelper.lib.addon.plugin import get_setting
    from tmdbhelper.lib.addon.plugin import get_localized
    players_url = get_setting('players_url', 'str')
    players_url = Dialog().input(get_localized(32313), defaultt=players_url)
    if not Dialog().yesno(
            get_localized(32032),
            get_localized(32314).format(players_url)):
        return
    set_setting('players_url', players_url, 'str')
    downloader = Downloader(
        extract_to='special://profile/addon_data/plugin.video.themoviedb.helper/players',
        download_url=players_url)
    downloader.get_extracted_zip()


def set_defaultplayer(**kwargs):
    from tmdbhelper.lib.player.players import PlayersFactory
    from tmdbhelper.lib.addon.plugin import set_setting
    tmdb_type = kwargs.get('set_defaultplayer')
    setting_name = 'default_player_movies' if tmdb_type == 'movie' else 'default_player_episodes'
    default_player = PlayersFactory(tmdb_type).select_default()
    if not default_player:
        return
    if not default_player.get('file') or not default_player.get('mode'):
        return set_setting(setting_name, '', 'str')
    set_setting(setting_name, f'{default_player["file"]} {default_player["mode"]}', 'str')
