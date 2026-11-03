# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html


def log_request(**kwargs):
    if kwargs.get('log_request', '').lower() == 'trakt':
        from tmdbhelper.lib.script.method.trakt import run_trakt_diagnostic
        return run_trakt_diagnostic('log_request', path=kwargs.get('url'))
    import xbmcvfs
    from json import dumps
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.dialog import BusyDialog
    from tmdbhelper.lib.api.tmdb.api import TMDb
    from tmdbhelper.lib.files.futils import validify_filename
    from tmdbhelper.lib.files.futils import dumps_to_file
    with BusyDialog():
        kwargs['response'] = None
        if not kwargs.get('url'):
            kwargs['url'] = Dialog().input('URL')
        if not kwargs['url']:
            return
        kwargs['response'] = TMDb().get_response_json(kwargs['url'])
        if not kwargs['response']:
            Dialog().ok(kwargs['log_request'].capitalize(), f'{kwargs["url"]}\nNo Response!')
            return
        filename = validify_filename(f'{kwargs["log_request"]}_{kwargs["url"]}.json')
        dumps_to_file(kwargs, 'log_request', filename)
        msg = (
            f'[B]{kwargs["url"]}[/B]\n\n{xbmcvfs.translatePath("special://profile/addon_data/")}\n'
            f'plugin.video.themoviedb.helper/log_request\n{filename}')
        Dialog().ok(kwargs['log_request'].capitalize(), msg)
        Dialog().textviewer(filename, dumps(kwargs['response'], indent=2))
