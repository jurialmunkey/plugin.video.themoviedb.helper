from xbmcgui import ListItem as KodiListItem
from jurialmunkey.parser import try_int, merge_two_dicts
from infotagger.listitem import ListItemInfoTag
from tmdbhelper.lib.addon.consts import PARAM_WIDGETS_RELOAD, PARAM_WIDGETS_RELOAD_FORCED
from tmdbhelper.lib.addon.plugin import ADDONPATH, PLUGINPATH, convert_media_type, get_condvisibility, get_localized, encode_url, get_flatseasons_info_param, GlobalSettingsDict
from tmdbhelper.lib.addon.tmdate import is_unaired_timestamp
from jurialmunkey.window import get_property

""" Lazyimports
from tmdbhelper.lib.items.context import ContextMenu
"""


global_setting = GlobalSettingsDict()
global_setting.route = {
    'is_skinshortcuts': (lambda: get_condvisibility("Window.IsVisible(script-skinshortcuts.xml)") or get_property('IsSkinShortcut'), None, ),
    'is_skinshortcuts_standard': (lambda: global_setting['is_skinshortcuts'] and get_property('IsStandardSkinShortcut'), None, ),
    'flatseasons_info_param': (get_flatseasons_info_param, None, )
}


def ListItem(*args, **kwargs):
    """ Factory to build ListItem object """
    factory = {
        'movie': _Movie,
        'tvshow': _Tvshow,
        'season': _Season,
        'episode': _Episode,
        'video': _Video,
        'set': _Collection,
        'studio': _Studio,
        'keyword': _Keyword,
        'person': _Person
    }

    try:
        mediatype = kwargs['infolabels'].pop('mediatype')
    except (KeyError, AttributeError, TypeError):
        mediatype = None

    if kwargs.get('next_page'):
        return _NextPage(*args, **kwargs)
    if kwargs.get('infoproperties', {}).get('tmdb_type') == 'person':
        return _Person(*args, **kwargs)
    try:
        return factory[mediatype](*args, **kwargs)
    except KeyError:
        return _ListItem(*args, **kwargs)


class _ListItem(object):

    mediatype = None
    context_additions = None
    playcount = None

    def __init__(
            self, label=None, label2=None, path=None, library=None, is_folder=True, params=None, next_page=None,
            parent_params=None, infolabels=None, infoproperties=None, art=None, cast=None,
            context_menu=None, stream_details=None, unique_ids=None,
            **kwargs):
        self.label = label or ''
        self.label2 = label2 or ''
        self.path = path or PLUGINPATH
        self.params = params or {}
        self.parent_params = parent_params or {}
        self.library = library or 'video'
        self.is_folder = is_folder
        self.next_page = next_page

        self.infolabels = self.init_infolabels(infolabels)
        self.infoproperties = self.init_infoproperties(infoproperties)
        self.art = self.init_art(art)
        self.cast = self.init_cast(cast)
        self.context_menu = self.init_context_menu(context_menu)
        self.stream_details = self.init_stream_details(stream_details)
        self.unique_ids = self.init_unique_ids(unique_ids)

    @staticmethod
    def init_unique_ids(unique_ids):
        unique_ids = unique_ids or {}
        return unique_ids

    @staticmethod
    def init_stream_details(stream_details):
        stream_details = stream_details or {}
        return stream_details

    @staticmethod
    def init_context_menu(context_menu):
        context_menu = context_menu or []
        return context_menu

    @staticmethod
    def init_cast(cast):
        cast = cast or []
        return cast

    @staticmethod
    def init_art(art):
        art = art or {}
        return art

    @staticmethod
    def init_infoproperties(infoproperties):
        infoproperties = infoproperties or {}
        return infoproperties

    def init_infolabels(self, infolabels):
        infolabels = infolabels or {}
        infolabels['mediatype'] = self.mediatype
        return infolabels

    @property
    def finalised_infolabels(self):
        self.infolabels['playcount'] = self.playcount
        return self.infolabels

    @property
    def finalised_infoproperties(self):
        return self.infoproperties

    @property
    def finalised_art(self):
        self.art['icon'] = self.finalised_icon
        return self.art

    @property
    def finalised_icon(self):
        icon = self.art.get('icon')
        icon = icon or self.art.get('poster')
        icon = icon or f'{ADDONPATH}/resources/icons/themoviedb/default.png'
        return icon

    @property
    def trakt_type(self):
        return convert_media_type(self.mediatype, 'trakt')

    @property
    def tmdb_type(self):
        return convert_media_type(self.mediatype, 'tmdb', parent_type=True)

    @property
    def ftv_type(self):
        return convert_media_type(self.mediatype, 'ftv')

    @property
    def ftv_id(self):
        return None

    @property
    def tmdb_id(self):
        return self.unique_ids.get('tmdb')

    @property
    def season(self):
        return None

    @property
    def episode(self):
        return

    def format_unaired_label(self, format_label=None, no_date=True):
        return

    def set_details(self, details=None, reverse=False, override=False):
        if not details:
            return
        self.stream_details = merge_two_dicts(details.get('stream_details', {}), self.stream_details, reverse=reverse)
        self.infolabels = merge_two_dicts(details.get('infolabels', {}), self.infolabels, reverse=reverse)
        self.infoproperties = merge_two_dicts(details.get('infoproperties', {}), self.infoproperties, reverse=reverse)
        self.art = merge_two_dicts(details.get('art', {}), self.art, reverse=reverse)
        self.unique_ids = merge_two_dicts(details.get('unique_ids', {}), self.unique_ids, reverse=reverse)
        self.cast = self.cast or details.get('cast', [])
        if not override:
            return
        self.label = details.get('label') or self.label
        self.infolabels['title'] = details.get('infolabels', {}).get('title') or self.infolabels.get('title')
        self.infolabels['tvshowtitle'] = details.get('infolabels', {}).get('tvshowtitle') or self.infolabels.get('tvshowtitle')

    def _set_params_reroute_skinshortcuts(self):
        if not global_setting['is_skinshortcuts_standard']:
            self.params['widget'] = 'true'
        # Reroute sortable lists to display options in skinshortcuts
        if self.infoproperties.get('is_sortable'):
            self.params['parent_info'] = self.params['info']
            self.params['info'] = 'trakt_sortby'
        # Add param to empty search to ensure reloads
        if self.params.get('info') == 'search' and not self.params.get('query'):
            self.params['reload'] = 'forced'

    def set_params_reroute(self, extended=None, is_cacheonly=False):
        if not self.path.startswith(PLUGINPATH):
            return

        if global_setting['is_skinshortcuts']:
            self._set_params_reroute_skinshortcuts()

        # Reroute for extended sorting of trakt list by inprogress to open up next folder
        if extended == 'inprogress':
            self.params['info'] = 'trakt_upnext'

        # Reconfigure details item into play/browse etc.
        if self.params.get('info') == 'details':
            return self._set_params_reroute_details()

        # Copy some params to next folder path
        if not self.is_folder:
            return
        if is_cacheonly:
            self.params['cacheonly'] = is_cacheonly
            return

    def _set_params_reroute_details(self):
        return  # Done in child class

    def set_episode_label(self, format_label=None):
        return  # Done in child class

    def set_uids_to_info(self):
        for k, v in self.unique_ids.items():
            if not v:
                continue
            self.infoproperties[f'{k}_id'] = v

    def set_params_to_info(self, **kwargs):
        for k, v in self.params.items():
            if not k or not v:
                continue
            self.infoproperties[f'item.{k}'] = v
        if self.params.get('tmdb_type'):
            self.infoproperties['item.type'] = self.params['tmdb_type']
        for k, v in kwargs.items():
            self.infoproperties[k] = v

    def get_url(self):
        def _get_url(path, reload=None, widget=None, **params):
            url = encode_url(path, **params)
            reload_param = PARAM_WIDGETS_RELOAD_FORCED if reload == 'forced' else None  # Note reload not std builtin but param absorbed in kwargs
            if widget and widget.lower() == 'true':
                reload_param = PARAM_WIDGETS_RELOAD
                url = f'{url}&widget=true&{PARAM_WIDGETS_RELOAD}'
            if reload_param:
                url = f'{url}&{reload_param}'
            return url
        return _get_url(self.path, **self.params)

    def get_listitem(self, offscreen=True):
        self.infolabels['path'] = self.get_url()
        listitem = KodiListItem(label=self.label, label2=self.label2, path=self.infolabels['path'], offscreen=offscreen)
        return self.set_listitem(listitem)

    @property
    def finalised_context_menu(self):
        from tmdbhelper.lib.items.context import ContextMenu
        self.context_menu += ContextMenu(self).get()
        self.context_menu += self.context_additions or []
        return self.context_menu

    def set_infotag(self, listitem):
        if self.library != 'pictures':
            info_tag = ListItemInfoTag(listitem)
            info_tag.set_info(self.finalised_infolabels)
            info_tag.set_unique_ids(self.unique_ids)
            info_tag.set_cast(self.cast)
            info_tag.set_stream_details(self.stream_details)
            info_tag.set_resume_point(self.infoproperties)
        return listitem

    def set_properties(self, listitem):
        listitem.setProperties(self.finalised_infoproperties)
        return listitem

    def set_label2(self, listitem):
        listitem.setLabel2(self.label2)
        return listitem

    def set_art(self, listitem):
        listitem.setArt(self.finalised_art)
        return listitem

    def set_context_menu(self, listitem):
        listitem.addContextMenuItems(self.finalised_context_menu)
        return listitem

    def set_listitem(self, listitem):
        listitem = self.set_label2(listitem)
        listitem = self.set_art(listitem)
        listitem = self.set_infotag(listitem)
        listitem = self.set_properties(listitem)
        listitem = self.set_context_menu(listitem)
        return listitem


class _NextPage(_ListItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = get_localized(33078)
        self.art['icon'] = f'{ADDONPATH}/resources/icons/themoviedb/nextpage.png'
        self.art['landscape'] = f'{ADDONPATH}/resources/icons/themoviedb/nextpage_wide.png'
        self.infoproperties['specialsort'] = 'bottom'
        self.params = self.parent_params.copy()
        self.params['page'] = self.next_page
        self.params.pop('update_listing', None)  # Just in case we updated the listing for search results
        self.path = PLUGINPATH
        self.is_folder = True


class _Keyword(_ListItem):
    def _set_params_reroute_details(self):
        self.params['info'] = 'discover'
        self.params['tmdb_type'] = 'movie'
        self.params['with_keywords'] = self.unique_ids.get('tmdb')
        self.params['with_id'] = 'True'
        self.is_folder = True


class _Studio(_ListItem):
    def _set_params_reroute_details(self):
        self.params['info'] = 'discover'
        self.params['tmdb_type'] = 'movie'
        self.params['with_companies'] = self.unique_ids.get('tmdb')
        self.params['with_id'] = 'True'
        self.is_folder = True


class _Person(_ListItem):

    mediatype = 'video'  # Need to hack as video to allow info dialog

    def _set_params_reroute_details(self):
        self.params['info'] = 'related'
        self.params['tmdb_type'] = 'person'
        self.params['tmdb_id'] = self.unique_ids.get('tmdb')
        self.is_folder = False

    @property
    def tmdb_type(self):
        return 'person'


class _Collection(_ListItem):

    mediatype = 'set'

    def _set_params_reroute_details(self):
        self.params['info'] = 'collection'


class _Video(_ListItem):

    mediatype = 'video'

    def format_unaired_label(self, format_label=u'[COLOR=ffcc0000][I]{}[/I][/COLOR]', no_date=True):
        if not format_label:
            return
        if not is_unaired_timestamp(self.infolabels.get('premiered'), no_date):
            return
        self.label = format_label.format(self.label)
        return self.label

    def _set_params_reroute_default(self):
        self.params['info'] = 'play'
        if not global_setting['only_resolve_strm']:
            self.infoproperties['isPlayable'] = 'true'
        self.is_folder = False
        self.context_menu.insert(0, (
            '$ADDON[plugin.video.themoviedb.helper 32322]',
            f'RunPlugin({self.get_url()}&ignore_default=true)',))

    def _set_params_reroute_details(self):
        self._set_params_reroute_default()

    def _set_contextmenu_choosedefault(self, tmdb_type, tmdb_id, season=None, episode=None):
        name = self.infolabels.get('tvshowtitle') or self.infolabels.get('title') or self.label
        path = f'set_chosenplayer={name},tmdb_type={tmdb_type},tmdb_id={tmdb_id}'

        if season is not None:
            path = f'{path},season={season}'
            if episode is not None:
                path = f'{path},episode={episode}'

        self.context_menu.append((
            '$ADDON[plugin.video.themoviedb.helper 32476]',
            f'Runscript(plugin.video.themoviedb.helper,{path})',))


class _Movie(_Video):

    mediatype = 'movie'

    @property
    def ftv_id(self):
        return self.unique_ids.get('tmdb')

    @property
    def playcount(self):
        return try_int(self.infolabels.get('playcount'), fallback=None)

    def _set_params_reroute_details(self):
        self._set_contextmenu_choosedefault('movie', self.unique_ids.get('tmdb'))
        self._set_params_reroute_default()


class _Tvshow(_Video):

    mediatype = 'tvshow'

    @property
    def ftv_id(self):
        return self.unique_ids.get('tvdb')

    @property
    def playcount(self):
        return try_int(self.infolabels.get('playcount'), fallback=None)

    @property
    def totalepisodes(self):
        return try_int(self.infolabels.get('episode'), fallback=None)

    @property
    def totalseasons(self):
        return try_int(self.infolabels.get('season'), fallback=None)

    @property
    def watchedepisodes(self):
        if self.totalepisodes is None:
            return
        return try_int(self.infolabels.get('playcount'), fallback=None)

    @property
    def unwatchedepisodes(self):
        if self.watchedepisodes is None:
            return
        return self.totalepisodes - self.watchedepisodes

    @property
    def watchedprogress(self):
        if self.watchedepisodes is None:
            return
        return int(self.watchedepisodes * 100 / self.totalepisodes)

    @property
    def finalised_infoproperties(self):
        self.infoproperties['totalepisodes'] = self.totalepisodes
        self.infoproperties['watchedepisodes'] = self.watchedepisodes
        self.infoproperties['unwatchedepisodes'] = self.unwatchedepisodes
        self.infoproperties['watchedprogress'] = self.watchedprogress
        self.infoproperties['totalseasons'] = self.totalseasons
        return self.infoproperties
        # if ip['unwatchedepisodes']:
        #     playcount = 0
        # il['playcount'] = playcount

    def _set_params_reroute_details(self):
        self._set_contextmenu_choosedefault('tv', self.unique_ids.get('tmdb'))
        self.params['info'] = global_setting['flatseasons_info_param']


class _Season(_Tvshow):

    mediatype = 'season'

    @property
    def finalised_infoproperties(self):
        self.infoproperties['totalepisodes'] = self.totalepisodes
        self.infoproperties['watchedepisodes'] = self.watchedepisodes
        self.infoproperties['unwatchedepisodes'] = self.unwatchedepisodes
        self.infoproperties['watchedprogress'] = self.watchedprogress
        return self.infoproperties

    @property
    def ftv_id(self):
        return self.unique_ids.get('tvshow.tvdb')

    @property
    def tmdb_id(self):
        return self.unique_ids.get('tvshow.tmdb')

    @property
    def season(self):
        return self.infolabels.get('season')

    def _set_params_reroute_details(self):
        self._set_contextmenu_choosedefault('tv', self.unique_ids.get('tvshow.tmdb'), season=self.infolabels.get('season'))
        self.params['info'] = 'episodes'


class _Episode(_Tvshow):

    mediatype = 'episode'
    thumb_override = 0

    @property
    def landscape(self):
        return self.art.get('landscape') or self.art.get('tvshow.landscape')

    @property
    def fanart(self):
        return self.art.get('fanart') or self.art.get('tvshow.fanart')

    @property
    def thumb(self):
        if self.thumb_override == 2:
            return self.landscape or self.fanart
        if self.thumb_override == 1:
            return self.fanart
        return self.art.get('thumb')

    @property
    def finalised_art(self):
        self.art = super().finalised_art
        self.art['thumb'] = self.thumb
        return self.art

    @property
    def ftv_id(self):
        return self.unique_ids.get('tvshow.tvdb')

    @property
    def tmdb_id(self):
        return self.unique_ids.get('tvshow.tmdb')

    @property
    def season(self):
        return self.infolabels.get('season')

    @property
    def episode(self):
        return self.infolabels.get('episode')

    @property
    def finalised_infoproperties(self):
        return self.infoproperties

    def _set_params_reroute_details(self):
        self._set_contextmenu_choosedefault(
            'tv', self.unique_ids.get('tvshow.tmdb'),
            season=self.infolabels.get('season'),
            episode=self.infolabels.get('episode'))
        if (self.parent_params.get('info') == 'library_nextaired'
                and global_setting['nextaired_linklibrary']
                and self.infoproperties.get('tvshow.dbid')):
            self.path = f'videodb://tvshows/titles/{self.infoproperties["tvshow.dbid"]}/'
            self.params = {}
            self.is_folder = True
            return
        self._set_params_reroute_default()

    def set_episode_label(self, format_label=u'{season}x{episode:0>2}. {label}'):
        if self.infoproperties.pop('no_label_formatting', None):
            return
        season = try_int(self.infolabels.get('season', 0))
        episode = try_int(self.infolabels.get('episode', 0))
        if not episode:
            return
        self.label = format_label.format(season=season, episode=episode, label=self.infolabels.get('title', ''))
