# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

def update_players():
    from xbmcgui import Dialog
    from tmdbhelper.lib.files.downloader import Downloader
    from tmdbhelper.lib.addon.plugin import set_setting, get_setting, get_localized
    players_url = get_setting('players_url', 'str')
    players_url = Dialog().input(get_localized(32313), defaultt=players_url)
    if not Dialog().yesno(
        get_localized(32032),
        get_localized(32314).format(players_url)
    ):
        return
    set_setting('players_url', players_url, 'str')
    downloader = Downloader(
        extract_to='special://profile/addon_data/plugin.video.themoviedb.helper/players',
        download_url=players_url)
    downloader.get_extracted_zip()
