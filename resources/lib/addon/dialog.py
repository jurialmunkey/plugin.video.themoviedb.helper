from xbmcgui import Dialog


def kodi_notification(*args, **kwargs):
    return Dialog().notification(*args, **kwargs)
