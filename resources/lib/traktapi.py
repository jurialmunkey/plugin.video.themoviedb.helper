from trakt import Trakt
from json import loads, dumps
import resources.lib.utils as utils
import xbmcgui
import xbmcaddon


class traktAPI(object):
    def __init__(self, force=False):
        Trakt.configuration.defaults.client(
            id='e6fde6173adf3c6af8fd1b0694b9b84d7c519cefc24482310e1de06c6abe5467',
            secret='15119384341d9a61c751d8d515acbc0dd801001d4ebe85d3eef9885df80ee4d9')
        Trakt.on('oauth.token_refreshed', self.on_token_refreshed)
        Trakt.configuration.defaults.oauth(refresh=True)

        token = xbmcaddon.Addon().getSetting('trakt_token')
        token = loads(token) if token else None

        if token and type(token) is dict and token.get('access_token') and not force:
            self.authorization = token
        else:
            self.login()

    def login(self):
        with Trakt.configuration.http(timeout=90):
            code = Trakt['oauth/device'].code()
            if code and code.get('user_code'):
                self.progress = 0
                self.interval = code.get('interval', 0)
                self.expirein = code.get('expires_in', 0)
                poller = Trakt['oauth/device'].poll(**code)\
                    .on('aborted', self.on_aborted)\
                    .on('authenticated', self.on_authenticated)\
                    .on('expired', self.on_expired)\
                    .on('poll', self.on_poll)
                self.auth_dialog = xbmcgui.DialogProgress()
                self.auth_dialog.create(
                    'Trakt Authentication',
                    'Go to [B]https://trakt.tv/activate[/B]',
                    'Enter the code: [B]' + code.get('user_code') + '[/B]')
                poller.start(daemon=False)

    def on_token_refreshed(self, response):
        # OAuth token refreshed, save token for future calls
        self.authorization = response
        xbmcaddon.Addon().setSettingString('authorization', dumps(self.authorization))

    def on_aborted(self):
        """Triggered when device authentication was aborted (either with `DeviceOAuthPoller.stop()`
           or via the "poll" event)"""
        utils.kodi_log('Trakt Authentication Aborted!', 1)
        self.auth_dialog.close()

    def on_expired(self):
        """Triggered when the device authentication code has expired"""
        utils.kodi_log('Trakt Authentication Expired!', 1)
        self.auth_dialog.close()

    def on_authenticated(self, token):
        """Triggered when device authentication has been completed

        :param token: Authentication token details
        :type token: dict
        """
        self.authorization = token
        utils.kodi_log('Trakt Authenticated Successfully!', 1)
        xbmcaddon.Addon().setSettingString('trakt_token', dumps(token))
        self.auth_dialog.close()

    def on_poll(self, callback):
        """Triggered before each poll

        :param callback: Call with `True` to continue polling, or `False` to abort polling
        :type callback: func
        """

        # Continue polling
        if self.auth_dialog.iscanceled():
            callback(False)
            self.auth_dialog.close()
        else:
            self.progress += self.interval
            progress = (self.progress * 100) / self.expirein
            self.auth_dialog.update(progress)
            callback(True)

    def get_synclist(self, synclist, dbtype=None, keylist=[]):
        with Trakt.configuration.oauth.from_response(self.authorization):
            with Trakt.configuration.http(retry=True, timeout=90):
                if dbtype == 'movies':
                    items = Trakt[synclist].movies()
                else:
                    items = Trakt[synclist].shows()
            trakt_list = utils.listify_items(items)
            itemlist = []
            for i in trakt_list:
                itemlist.append(i.pk)
            return itemlist

    def get_itemlist(self, listpath, dbtype=None, keylist=['dummy']):
        with Trakt.configuration.oauth.from_response(self.authorization):
            with Trakt.configuration.http(retry=True, timeout=90):
                response = Trakt.http.get(listpath)
                items = response.json()
                itemlist = []
                for i in items:
                    for key in keylist:
                        item = None
                        myitem = i.get(key) or i
                        if myitem:
                            tmdbtype = 'tv' if key == 'show' else 'movie'
                            if myitem.get('ids', {}).get('imdb'):
                                item = ('imdb', myitem.get('ids', {}).get('imdb'), tmdbtype)
                            elif myitem.get('ids', {}).get('tvdb'):
                                item = ('tvdb', myitem.get('ids', {}).get('tvdb'), tmdbtype)
                            if item:
                                itemlist.append(item)
                return itemlist

    def get_listlist(self, listpath, key=None):
        with Trakt.configuration.oauth.from_response(self.authorization):
            with Trakt.configuration.http(retry=True, timeout=90):
                response = Trakt.http.get(listpath)
                items = response.json()
                itemlist = []
                for i in items:
                    item = i.get(key) or i
                    if item:
                        itemlist.append(item)
                return itemlist

    def get_usernameslug(self):
        with Trakt.configuration.oauth.from_response(self.authorization):
            with Trakt.configuration.http(retry=True, timeout=90):
                response = Trakt.http.get('users/settings')
                item = response.json()
                return item.get('user', {}).get('ids', {}).get('slug')
