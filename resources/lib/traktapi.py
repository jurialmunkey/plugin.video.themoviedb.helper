from trakt import Trakt
from json import loads, dumps
import resources.lib.utils as utils
from resources.lib.requestapi import RequestAPI
import xbmcgui
import xbmcaddon
import datetime


class traktAPI(RequestAPI):
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

    def get_request_url(self, *args, **kwargs):
        """
        Creates a url request string:
        """
        request = None
        for arg in args:
            if arg:  # Don't add empty args
                request = u'{0}/{1}'.format(request, arg) if request else arg
        for key, value in kwargs.items():
            if value:  # Don't add empty kwargs
                sep = '?' if '?' not in request else ''
                request = u'{0}{1}&{2}={3}'.format(request, sep, key, value)
        return request

    def get_response(self, *args, **kwargs):
        with Trakt.configuration.oauth.from_response(self.authorization):
            with Trakt.configuration.http(retry=True, timeout=90):
                return Trakt.http.get(self.get_request_url(*args, **kwargs))

    def get_itemlist(self, *args, **kwargs):
        keylist = kwargs.pop('keylist', ['dummy'])
        response = self.get_response(*args, **kwargs)
        itemlist = response.json()
        this_page = int(kwargs.get('page', 1))
        last_page = int(response.headers.get('X-Pagination-Page-Count', 0))
        next_page = ('next_page', this_page + 1, None) if this_page < last_page else False
        items = []
        for i in itemlist:
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
                        items.append(item)
        if next_page:
            items.append(next_page)
        return items

    def get_listlist(self, request, key=None):
        response = self.get_response(request).json()
        items = [i.get(key) or i for i in response if i.get(key) or i]
        return items

    def get_limitedlist(self, itemlist, itemtype, limit):
        items = []
        n = 0
        for i in itemlist:
            if limit and n >= limit:
                break
            item = (i.get(itemtype, {}).get('ids', {}).get('slug'), i.get(itemtype, {}).get('ids', {}).get('tmdb'))
            if item not in items:
                items.append(item)
                n += 1
        return items

    def get_mostwatched(self, userslug, itemtype, limit=None):
        history = self.get_response('users', userslug, 'watched', itemtype + 's').json()
        history = sorted(history, key=lambda i: i['plays'], reverse=True)
        return self.get_limitedlist(history, itemtype, limit)

    def get_recentlywatched(self, userslug, itemtype, limit=None):
        start_at = datetime.date.today() - datetime.timedelta(6 * 365 / 12)
        history = self.get_response('users', userslug, 'history', itemtype + 's', page=1, limit=200, start_at=start_at.strftime("%Y-%m-%d")).json()
        return self.get_limitedlist(history, itemtype, limit)

    def get_inprogress(self, userslug, limit=None):
        """
        Looks at user's most recently watched 200 episodes in last 6 months
        Adds each unique show to list in order then checks if show has an upnext episode
        Returns list of tmdb_ids representing shows with upnext episodes in recently watched order
        """
        recentshows = self.get_recentlywatched(userslug, 'show')
        items = []
        n = 0
        for i in recentshows:
            if limit and n >= limit:
                break
            progress = self.get_upnext(i[0], True)
            if progress and progress.get('next_episode'):
                utils.kodi_log(progress.get('next_episode'), 1)
                items.append(i)
                n += 1
        return items

    def get_upnext(self, show_id, response_only=False):
        request = 'shows/{0}/progress/watched'.format(show_id)
        response = self.get_response(request).json()
        reset_at = utils.convert_timestamp(response.get('reset_at')) if response.get('reset_at') else None
        seasons = response.get('seasons', [])
        items = []
        for season in seasons:
            s_num = season.get('number')
            for episode in season.get('episodes', []):
                item = None
                e_num = episode.get('number')
                if episode.get('completed'):
                    if reset_at and utils.convert_timestamp(episode.get('last_watched_at')) < reset_at:
                        item = (s_num, e_num)
                else:
                    item = (s_num, e_num)
                if item:
                    if response_only:
                        return response
                    items.append(item)
        if not response_only:
            return items

    def get_usernameslug(self):
        item = self.get_response('users/settings').json()
        return item.get('user', {}).get('ids', {}).get('slug')

    def get_traktslug(self, item_type, id_type, id):
        item = self.get_response('search', id_type, id, '?' + item_type).json()
        return item[0].get(item_type, {}).get('ids', {}).get('slug')
