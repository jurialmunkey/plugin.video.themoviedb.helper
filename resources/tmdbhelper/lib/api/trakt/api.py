import random
from xbmc import Monitor
from xbmcgui import Dialog, DialogProgress
from tmdbhelper.lib.files.futils import json_loads as data_loads
from tmdbhelper.lib.files.futils import json_dumps as data_dumps
from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.plugin import get_localized, get_setting, ADDONPATH
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp
from tmdbhelper.lib.files.bcache import use_simple_cache
from tmdbhelper.lib.items.pages import PaginatedItems, get_next_page
from tmdbhelper.lib.api.request import RequestAPI
from tmdbhelper.lib.api.trakt.items import TraktItems
from tmdbhelper.lib.api.trakt.decorators import is_authorized, use_activity_cache
from tmdbhelper.lib.api.trakt.progress import _TraktProgress
from tmdbhelper.lib.api.trakt.sync import _TraktSync
from tmdbhelper.lib.addon.logger import kodi_log, TimerFunc
from tmdbhelper.lib.addon.consts import CACHE_SHORT, CACHE_LONG
from tmdbhelper.lib.addon.thread import has_property_lock
from tmdbhelper.lib.api.api_keys.trakt import CLIENT_ID, CLIENT_SECRET, USER_TOKEN
from timeit import default_timer as timer


API_URL = 'https://api.trakt.tv/'


def get_sort_methods(info=None):
    items = [
        {
            'name': f'{get_localized(32287)}: {get_localized(32451)} {get_localized(32286)}',
            'params': {'sort_by': 'rank', 'sort_how': 'asc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(32452)} {get_localized(32286)}',
            'params': {'sort_by': 'rank', 'sort_how': 'desc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(20382).capitalize()}',
            'params': {'sort_by': 'added', 'sort_how': 'desc'},
            'blocklist': ('trakt_collection',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32473)}',
            'params': {'sort_by': 'collected', 'sort_how': 'desc'},
            'allowlist': ('trakt_collection',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(369)} (A-Z)',
            'params': {'sort_by': 'title', 'sort_how': 'asc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(369)} (Z-A)',
            'params': {'sort_by': 'title', 'sort_how': 'desc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(16102)}',
            'params': {'sort_by': 'watched', 'sort_how': 'desc', 'extended': 'sync'},
            'allowlist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(563)}',
            'params': {'sort_by': 'percentage', 'sort_how': 'desc', 'extended': 'full'},
            'allowlist': ('trakt_userlist', 'trakt_watchlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(345)} {get_localized(584)}',
            'params': {'sort_by': 'year', 'sort_how': 'asc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(345)} {get_localized(585)}',
            'params': {'sort_by': 'year', 'sort_how': 'desc'}},
        {
            'name': f'{get_localized(32287)}: {get_localized(32453).capitalize()}',
            'params': {'sort_by': 'plays', 'sort_how': 'asc', 'extended': 'sync'},
            'allowlist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32205)}',
            'params': {'sort_by': 'plays', 'sort_how': 'desc', 'extended': 'sync'},
            'allowlist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32242)} {get_localized(584)}',
            'params': {'sort_by': 'released', 'sort_how': 'asc', 'extended': 'full'},
            'allowlist': ('trakt_userlist', 'trakt_watchlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32242)} {get_localized(585)}',
            'params': {'sort_by': 'released', 'sort_how': 'desc', 'extended': 'full'},
            'allowlist': ('trakt_userlist', 'trakt_watchlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32454)} {get_localized(2050)}',
            'params': {'sort_by': 'runtime', 'sort_how': 'asc', 'extended': 'full'},
            'allowlist': ('trakt_userlist', 'trakt_watchlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32455)} {get_localized(2050)}',
            'params': {'sort_by': 'runtime', 'sort_how': 'desc', 'extended': 'full'},
            'allowlist': ('trakt_userlist', 'trakt_watchlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(205)}',
            'params': {'sort_by': 'votes', 'sort_how': 'desc', 'extended': 'full'},
            'allowlist': ('trakt_userlist', 'trakt_watchlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(32175)}',
            'params': {'sort_by': 'popularity', 'sort_how': 'desc', 'extended': 'full'},
            'allowlist': ('trakt_userlist', 'trakt_watchlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(575)}',
            'params': {'sort_by': 'watched', 'sort_how': 'desc', 'extended': 'inprogress'},
            'allowlist': ('trakt_userlist',)},
        {
            'name': f'{get_localized(32287)}: {get_localized(590)}',
            'params': {'sort_by': 'random'}}]

    return [
        i for i in items
        if (
            ('allowlist' not in i or info in i['allowlist'])
            and ('blocklist' not in i or info not in i['blocklist'])
        )]


class _TraktLists():
    def _merge_sync_sort(self, items):
        """ Get sync dict sorted by slugs then merge slug into list """
        sync = {}
        sync.update(self.get_sync('watched', 'show', 'slug', extended='full'))
        sync.update(self.get_sync('watched', 'movie', 'slug'))
        return [dict(i, **sync.get(i.get(i.get('type'), {}).get('ids', {}).get('slug'), {})) for i in items]

    def _filter_inprogress(self, items):
        """ Filter list so that it only returns inprogress shows """
        inprogress = self._get_inprogress_shows() or []
        inprogress = [i['show']['ids']['slug'] for i in inprogress if i.get('show', {}).get('ids', {}).get('slug')]
        if not inprogress:
            return
        items = [i for i in items if i.get('show', {}).get('ids', {}).get('slug') in inprogress]
        return items

    @use_simple_cache(cache_days=CACHE_SHORT)
    def get_sorted_list(self, path, sort_by=None, sort_how=None, extended=None, trakt_type=None, permitted_types=None, cache_refresh=False):
        response = self.get_response(path, extended=extended, limit=4095)
        if not response:
            return

        if extended == 'sync':
            items = self._merge_sync_sort(response.json())
        elif extended == 'inprogress':
            items = self._filter_inprogress(self._merge_sync_sort(response.json()))
        else:
            items = response.json()

        return TraktItems(items, headers=response.headers).build_items(
            sort_by=sort_by or response.headers.get('x-sort-by'),
            sort_how=sort_how or response.headers.get('x-sort-how'),
            permitted_types=permitted_types)

    @use_simple_cache(cache_days=CACHE_SHORT)
    def get_simple_list(self, *args, trakt_type=None, **kwargs):
        response = self.get_response(*args, **kwargs)
        if not response:
            return
        return TraktItems(response.json(), headers=response.headers, trakt_type=trakt_type).configure_items()

    @is_authorized
    def get_mixed_list(self, path, trakt_types: list, limit: int = None, extended: str = None, authorize=False):
        """ Returns a randomised simple list which combines movies and shows
        path uses {trakt_type} as format substitution for trakt_type in trakt_types
        """
        items = []
        limit = limit or self.item_limit
        for trakt_type in trakt_types:
            response = self.get_simple_list(
                path.format(trakt_type=trakt_type), extended=extended, page=1, limit=limit * 2, trakt_type=trakt_type) or {}
            items += response.get('items') or []
        if not items:
            return
        if len(items) <= limit:
            return items
        return random.sample(items, limit)

    @is_authorized
    def get_basic_list(self, path, trakt_type, page: int = 1, limit: int = None, params=None, sort_by=None, sort_how=None, extended=None, authorize=False, randomise=False, always_refresh=True):
        cache_refresh = True if always_refresh and try_int(page, fallback=1) == 1 else False
        limit = limit or self.item_limit
        if randomise:
            response = self.get_simple_list(
                path, extended=extended, page=1, limit=limit * 2, trakt_type=trakt_type)
        elif sort_by is not None:  # Sorted list manually paginated because need to sort first
            response = self.get_sorted_list(path, sort_by, sort_how, extended, cache_refresh=cache_refresh)
            response = PaginatedItems(items=response['items'], page=page, limit=limit).get_dict()
        else:  # Unsorted lists can be paginated by the API
            response = self.get_simple_list(path, extended=extended, page=page, limit=limit, trakt_type=trakt_type)
        if not response:
            return
        if randomise and len(response['items']) > limit:
            return random.sample(response['items'], limit)
        return response['items'] + get_next_page(response['headers'])

    @is_authorized
    def get_stacked_list(self, path, trakt_type, page: int = 1, limit: int = None, params=None, sort_by=None, sort_how=None, extended=None, authorize=False, always_refresh=True, **kwargs):
        """ Get Basic list but stack repeat TV Shows """
        limit = limit or self.item_limit
        cache_refresh = True if always_refresh and try_int(page, fallback=1) == 1 else False
        response = self.get_simple_list(path, extended=extended, limit=4095, trakt_type=trakt_type, cache_refresh=cache_refresh)
        response['items'] = self._stack_calendar_tvshows(response['items'])
        response = PaginatedItems(items=response['items'], page=page, limit=limit).get_dict()
        if response:
            return response['items'] + get_next_page(response['headers'])

    @is_authorized
    def get_custom_list(self, list_slug, user_slug=None, page: int = 1, limit: int = None, params=None, authorize=False, sort_by=None, sort_how=None, extended=None, owner=False, always_refresh=True):
        limit = limit or self.item_limit
        if user_slug == 'official':
            path = f'lists/{list_slug}/items'
        else:
            path = f'users/{user_slug or "me"}/lists/{list_slug}/items'
        # Refresh cache on first page for user list because it might've changed
        cache_refresh = True if always_refresh and try_int(page, fallback=1) == 1 else False
        sorted_items = self.get_sorted_list(
            path, sort_by, sort_how, extended,
            permitted_types=['movie', 'show', 'person', 'episode'],
            cache_refresh=cache_refresh) or {}
        paginated_items = PaginatedItems(
            items=sorted_items.get('items', []), page=page, limit=limit)
        return {
            'items': paginated_items.items,
            'movies': sorted_items.get('movies', []),
            'shows': sorted_items.get('shows', []),
            'persons': sorted_items.get('persons', []),
            'next_page': paginated_items.next_page}

    @use_activity_cache(cache_days=CACHE_SHORT)
    def _get_sync_list(self, sync_type, trakt_type, sort_by=None, sort_how=None, decorator_cache_refresh=False, extended=None, filters=None):
        get_property('TraktSyncLastActivities.Expires', clear_property=True)  # Wipe last activities cache to update now
        func = TraktItems(items=self.get_sync(sync_type, trakt_type, extended=extended), trakt_type=trakt_type).build_items
        return func(sort_by, sort_how, filters=filters)

    def get_sync_list(self, sync_type, trakt_type, page: int = 1, limit: int = None, params=None, sort_by=None, sort_how=None, next_page=True, always_refresh=True, extended=None, filters=None):
        limit = limit or self.sync_item_limit
        cache_refresh = True if always_refresh and try_int(page, fallback=1) == 1 else False
        response = self._get_sync_list(sync_type, trakt_type, sort_by=sort_by, sort_how=sort_how, decorator_cache_refresh=cache_refresh, extended=extended, filters=filters)
        if not response:
            return
        response = PaginatedItems(items=response['items'], page=page, limit=limit)
        return response.items if not next_page else response.items + response.next_page

    @is_authorized
    def get_list_of_lists(self, path, page: int = 1, limit: int = 250, authorize=False, next_page=True, sort_likes=False):
        response = self.get_response(path, page=page, limit=limit)
        if not response:
            return
        items = []
        sorted_list = sorted(response.json(), key=lambda i: i.get('likes', 0) or i.get('list', {}).get('likes', 0), reverse=True) if sort_likes else response.json()
        for i in sorted_list:
            if i.get('list') and i['list'].get('name'):
                i = i['list']
            elif not i.get('name'):
                continue

            i_name = i.get('name')
            i_usr = i.get('user') or {}
            i_ids = i.get('ids') or {}
            i_usr_ids = i_usr.get('ids') or {}
            i_usr_slug = 'official' if i.get('type') == 'official' else i_usr_ids.get('slug')
            i_lst_slug = i_ids.get('slug')
            i_lst_trakt = i_ids.get('trakt')

            item = {}
            item['label'] = f"{i.get('name')}"
            item['infolabels'] = {'plot': i.get('description'), 'studio': [i_usr.get('name') or i_usr_ids.get('slug')]}
            item['infoproperties'] = {k: v for k, v in i.items() if v and type(v) not in [list, dict]}
            item['art'] = {}
            item['params'] = {
                'info': 'trakt_userlist',
                'list_name': i_name,
                'list_slug': i_lst_slug,
                'user_slug': i_usr_slug,
                'plugin_category': i_name}
            item['unique_ids'] = {
                'trakt': i_lst_trakt,
                'slug': i_lst_slug,
                'user': i_usr_slug}
            item['infoproperties']['is_sortable'] = 'True'

            # Add sort methods
            item['context_menu'] = [(
                get_localized(32309),
                u'Runscript(plugin.video.themoviedb.helper,sort_list,{})'.format(
                    u','.join(f'{k}={v}' for k, v in item['params'].items())))]

            # Add library context menu
            item['context_menu'] += [(
                get_localized(20444), u'Runscript(plugin.video.themoviedb.helper,{})'.format(
                    u'user_list={list_slug},user_slug={user_slug}'.format(**item['params'])))]

            # Unlike list context menu
            if path.startswith('users/likes'):
                item['context_menu'] += [(
                    get_localized(32319), u'Runscript(plugin.video.themoviedb.helper,{},delete)'.format(
                        u'like_list={list_slug},user_slug={user_slug}'.format(**item['params'])))]

            # Like list context menu
            elif path.startswith('lists/'):
                item['context_menu'] += [(
                    get_localized(32315), u'Runscript(plugin.video.themoviedb.helper,{})'.format(
                        u'like_list={list_slug},user_slug={user_slug}'.format(**item['params'])))]

            # Owner of list so set param to allow deleting later
            else:
                item['params']['owner'] = 'true'
                item['context_menu'] += [(
                    get_localized(118), u'Runscript(plugin.video.themoviedb.helper,{})'.format(
                        u'rename_list={list_slug}'.format(**item['params'])))]
                item['context_menu'] += [(
                    get_localized(117), u'Runscript(plugin.video.themoviedb.helper,{})'.format(
                        u'delete_list={list_slug}'.format(**item['params'])))]

            items.append(item)
        if not next_page:
            return items
        return items + get_next_page(response.headers)

    @is_authorized
    def like_userlist(self, user_slug=None, list_slug=None, confirmation=False, delete=False):
        func = self.delete_response if delete else self.post_response
        response = func('users', user_slug, 'lists', list_slug, 'like')
        if confirmation:
            affix = get_localized(32320) if delete else get_localized(32321)
            body = [
                get_localized(32316).format(affix),
                get_localized(32168).format(list_slug, user_slug)] if response.status_code == 204 else [
                get_localized(32317).format(affix),
                get_localized(32168).format(list_slug, user_slug),
                get_localized(32318).format(response.status_code)]
            Dialog().ok(get_localized(32315), '\n'.join(body))
        if response.status_code == 204:
            return response


class TraktAPI(RequestAPI, _TraktSync, _TraktLists, _TraktProgress):

    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    user_token = USER_TOKEN

    def __init__(
            self,
            client_id=None,
            client_secret=None,
            user_token=None,
            force=False,
            page_length=1):
        super(TraktAPI, self).__init__(req_api_url=API_URL, req_api_name='TraktAPI', timeout=20)
        self.authorization = ''
        self.attempted_login = False
        self.dialog_noapikey_header = f'{get_localized(32007)} {self.req_api_name} {get_localized(32011)}'
        self.dialog_noapikey_text = get_localized(32012)
        TraktAPI.client_id = client_id or self.client_id
        TraktAPI.client_secret = client_secret or self.client_secret
        TraktAPI.user_token = user_token or self.user_token
        self.headers = {'trakt-api-version': '2', 'trakt-api-key': self.client_id, 'Content-Type': 'application/json'}
        self.last_activities = {}
        self.sync_activities = {}
        self.sync = {}
        self.sync_item_limit = 20 * max(get_setting('pagemulti_sync', 'int'), page_length)
        self.item_limit = 20 * max(get_setting('pagemulti_trakt', 'int'), page_length)
        self.login() if force else self.authorize()

    def authorize(self, login=False):
        def _get_token():
            token = self.get_stored_token()
            if not token.get('access_token'):
                return
            self.authorization = token
            self.headers['Authorization'] = f'Bearer {self.authorization.get("access_token")}'
            return token

        def _check_auth():
            url = 'https://api.trakt.tv/sync/last_activities'
            response = self.get_simple_api_request(url, headers=self.headers)
            try:
                return response.status_code
            except AttributeError:
                return

        # Already got authorization so return credentials
        if self.authorization:
            return self.authorization

        # Check for saved credentials from previous login
        token = _get_token()

        # No saved credentials and user trying to use a feature that requires authorization so ask them to login
        if not token and login and not self.attempted_login:
            if Dialog().yesno(
                    self.dialog_noapikey_header, self.dialog_noapikey_text,
                    nolabel=get_localized(222), yeslabel=get_localized(186)):
                self.login()
            self.attempted_login = True

        # First time authorization in this session so let's confirm
        if (
                self.authorization
                and get_property('TraktIsAuth') != 'True'
                and not get_timestamp(get_property('TraktRefreshTimeStamp', is_type=float) or 0)):

            # Wait if another thread is checking authorization
            if has_property_lock('TraktCheckingAuth'):
                if get_property('TraktIsDown') == 'True':
                    return  # Trakt is down so do nothing
                _get_token()  # Get the token set in the other thread
                return self.authorization  # Another thread checked token so return

            # Set a thread lock property
            get_property('TraktCheckingAuth', 1)

            # Trakt was previously down so check again
            if get_property('TraktIsDown') == 'True' and _check_auth() not in [None, 500, 503]:
                get_property('TraktIsDown', clear_property=True)

            if get_property('TraktIsDown') != 'True':
                kodi_log('Trakt authorization check started', 1)

                # Check if we can get a response from user account
                with TimerFunc('Trakt authorization check took', inline=True) as tf:
                    response = _check_auth()

                    # Unauthorised so attempt a refresh
                    if response in [None, 401]:
                        kodi_log('Trakt unauthorized!', 1)
                        self.authorization = self.refresh_token()

                    # Trakt database is down
                    if response in [500, 503]:
                        kodi_log('Trakt is currently down!', 1)
                        get_property('TraktIsDown', 'True')

                    # Have a token and it worked! Auth confirmed.
                    elif self.authorization:
                        kodi_log('Trakt user account authorized', 1)
                        get_property('TraktIsAuth', 'True')

                        if get_setting('startup_notifications'):
                            total_time = timer() - tf.timer_a
                            Dialog().notification('TMDbHelper', f'Trakt authorized in {total_time:.3f}s', icon=f'{ADDONPATH}/icon.png')

            get_property('TraktCheckingAuth', clear_property=True)

        return self.authorization

    def get_stored_token(self):
        try:
            token = data_loads(self.user_token.value) or {}
        except Exception as exc:
            token = {}
            kodi_log(exc, 1)
        return token

    def logout(self):
        token = self.get_stored_token()

        if not Dialog().yesno(get_localized(32212), get_localized(32213)):
            return

        if token:
            response = self.get_api_request('https://api.trakt.tv/oauth/revoke', postdata={
                'token': token.get('access_token', ''),
                'client_id': self.client_id,
                'client_secret': self.client_secret})
            if response and response.status_code == 200:
                msg = get_localized(32216)
                self.user_token.value = ''
            else:
                msg = get_localized(32215)
        else:
            msg = get_localized(32214)

        Dialog().ok(get_localized(32212), msg)

    def login(self):
        self.code = self.get_api_request_json('https://api.trakt.tv/oauth/device/code', postdata={'client_id': self.client_id})
        if not self.code.get('user_code') or not self.code.get('device_code'):
            return  # TODO: DIALOG: Authentication Error
        self.progress = 0
        self.interval = self.code.get('interval', 5)
        self.expires_in = self.code.get('expires_in', 0)
        self.auth_dialog = DialogProgress()
        self.auth_dialog.create(get_localized(32097), f'{get_localized(32096)}\n{get_localized(32095)}: [B]{self.code.get("user_code")}[/B]')
        self.poller()

    def refresh_token(self):
        # Check we haven't attempted too many refresh attempts
        refresh_attempts = try_int(get_property('TraktRefreshAttempts')) + 1
        if refresh_attempts > 5:
            kodi_log('Trakt Unauthorised!\nExceeded refresh_token attempt limit\nSuppressing retries for 10 minutes', 1)
            get_property('TraktRefreshTimeStamp', set_timestamp(600))
            get_property('TraktRefreshAttempts', 0)  # Reset refresh attempts
            return
        get_property('TraktRefreshAttempts', refresh_attempts)

        kodi_log('Attempting to refresh Trakt token', 2)
        if not self.authorization or not self.authorization.get('refresh_token'):
            kodi_log('Trakt refresh token not found!', 1)
            return
        postdata = {
            'refresh_token': self.authorization.get('refresh_token'),
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'grant_type': 'refresh_token'}
        self.authorization = self.get_api_request_json('https://api.trakt.tv/oauth/token', postdata=postdata)
        if not self.authorization or not self.authorization.get('access_token'):
            kodi_log('Failed to refresh Trakt token!', 2)
            return
        self.on_authenticated(auth_dialog=False)
        kodi_log('Trakt token refreshed', 1)
        return self.authorization

    def poller(self):
        if not self.on_poll():
            self.on_aborted()
            return
        if self.expires_in <= self.progress:
            self.on_expired()
            return
        self.authorization = self.get_api_request_json('https://api.trakt.tv/oauth/device/token', postdata={'code': self.code.get('device_code'), 'client_id': self.client_id, 'client_secret': self.client_secret})
        if self.authorization:
            self.on_authenticated()
            return
        Monitor().waitForAbort(self.interval)
        if Monitor().abortRequested():
            return
        self.poller()

    def on_aborted(self):
        """Triggered when device authentication was aborted"""
        kodi_log(u'Trakt authentication aborted!', 1)
        self.auth_dialog.close()

    def on_expired(self):
        """Triggered when the device authentication code has expired"""
        kodi_log(u'Trakt authentication expired!', 1)
        self.auth_dialog.close()

    def on_authenticated(self, auth_dialog=True):
        """Triggered when device authentication has been completed"""
        kodi_log(u'Trakt authenticated successfully!', 1)
        self.user_token.value = data_dumps(self.authorization)
        self.headers['Authorization'] = f'Bearer {self.authorization.get("access_token")}'
        if auth_dialog:
            self.auth_dialog.close()

    def on_poll(self):
        """Triggered before each poll"""
        if self.auth_dialog.iscanceled():
            self.auth_dialog.close()
            return False
        else:
            self.progress += self.interval
            progress = (self.progress * 100) / self.expires_in
            self.auth_dialog.update(int(progress))
            return True

    def delete_response(self, *args, **kwargs):
        return self.get_simple_api_request(
            self.get_request_url(*args, **kwargs),
            headers=self.headers,
            method='delete')

    def post_response(self, *args, postdata=None, response_method='post', **kwargs):
        return self.get_simple_api_request(
            self.get_request_url(*args, **kwargs),
            headers=self.headers,
            postdata=data_dumps(postdata) if postdata else None,
            method=response_method)

    def get_response(self, *args, **kwargs):
        return self.get_api_request(self.get_request_url(*args, **kwargs), headers=self.headers)

    def get_response_json(self, *args, **kwargs):
        try:
            return self.get_api_request(self.get_request_url(*args, **kwargs), headers=self.headers).json()
        except ValueError:
            return {}
        except AttributeError:
            return {}

    def _get_id(self, unique_id, id_type, trakt_type, output_type=None, output_trakt_type=None, season_episode_check=None):

        response = self.get_request_lc('search', id_type, unique_id, type=trakt_type)

        for i in response:
            try:
                if i['type'] != trakt_type:
                    continue
                if f'{i[trakt_type]["ids"][id_type]}' != f'{unique_id}':
                    continue
                if trakt_type == 'episode' and season_episode_check is not None:
                    if f'{i["episode"]["season"]}' != f'{season_episode_check[0]}':
                        continue
                    if f'{i["episode"]["number"]}' != f'{season_episode_check[1]}':
                        continue

                if not output_type:
                    return i[output_trakt_type or trakt_type]['ids']
                return i[output_trakt_type or trakt_type]['ids'][output_type]

            except (TypeError, KeyError):
                continue

    def get_id(self, unique_id, id_type, trakt_type, output_type=None, output_trakt_type=None, season_episode_check=None):
        """
        id_type: imdb, tmdb, trakt, tvdb
        trakt_type: movie, show, episode, person, list
        output_type: trakt, slug, imdb, tmdb, tvdb
        output_trakt_type: optionally change trakt_type for output

        Example usage: self.get_id(1234, 'tmdb', 'episode', 'slug', 'show')
            -- gets trakt slug of the parent show for the episode with tmdb id 1234
        """
        cache_name = f'trakt_get_id.{id_type}.{unique_id}.{trakt_type}.{output_type}'

        # Some plugins incorrectly put TMDb ID for the **tvshow** in the episode instead of the **episode** ID
        # season_episode_check tuple of season/episode numbers is used to bandaid against incorrect metadata
        if trakt_type == 'episode' and season_episode_check is not None:
            cache_name = f'{cache_name}.{season_episode_check[0]}.{season_episode_check[1]}'

        # Avoid unnecessary extra API calls by only adding output type to cache name if it differs from input type
        if output_trakt_type and output_trakt_type != trakt_type:
            cache_name = f'{cache_name}.{output_trakt_type}'

        return self._cache.use_cache(
            self._get_id, unique_id, id_type, trakt_type=trakt_type, output_type=output_type, output_trakt_type=output_trakt_type,
            season_episode_check=season_episode_check,
            cache_name=cache_name,
            cache_days=CACHE_LONG)

    def get_details(self, trakt_type, id_num, season=None, episode=None, extended='full'):
        if not season or not episode:
            return self.get_request_lc(trakt_type + 's', id_num, extended=extended)
        return self.get_request_lc(trakt_type + 's', id_num, 'seasons', season, 'episodes', episode, extended=extended)

    @use_simple_cache(cache_days=CACHE_SHORT)
    def get_imdb_top250(self, id_type=None, trakt_type='movie'):
        paths = {
            'movie': 'users/justin/lists/imdb-top-rated-movies/items',
            'show': 'users/justin/lists/imdb-top-rated-tv-shows/items'}
        try:
            response = self.get_response(paths[trakt_type], limit=4095)
            sorted_items = TraktItems(response.json() if response else []).sort_items('rank', 'asc') or []
            return [i[trakt_type]['ids'][id_type] for i in sorted_items]
        except KeyError:
            return []

    @use_simple_cache(cache_days=CACHE_SHORT)
    def get_ratings(self, trakt_type, imdb_id=None, trakt_id=None, slug_id=None, season=None, episode=None):
        slug = slug_id or trakt_id or imdb_id
        if not slug:
            return
        if episode and season:
            url = f'shows/{slug}/seasons/{season}/episodes/{episode}/ratings'
        elif season:
            url = f'shows/{slug}/seasons/{season}/ratings'
        else:
            url = f'{trakt_type}s/{slug}/ratings'
        response = self.get_response_json(url)
        if not response:
            return
        return {
            'trakt_rating': f'{response.get("rating") or 0.0:0.1f}',
            'trakt_votes': f'{response.get("votes") or 0.0:0,.0f}'}
