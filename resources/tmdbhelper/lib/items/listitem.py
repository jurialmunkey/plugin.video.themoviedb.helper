from xbmcgui import ListItem as KodiListItem
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int, merge_two_dicts, boolean
from infotagger.listitem import ListItemInfoTag
from tmdbhelper.lib.addon.consts import PARAM_WIDGETS_RELOAD, PARAM_WIDGETS_RELOAD_FORCED
from tmdbhelper.lib.addon.plugin import ADDONPATH, PLUGINPATH, get_condvisibility, get_localized, encode_url, get_flatseasons_info_param, GlobalSettingsDict
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
        'image': _Image,
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


class BuildURL:
    def __init__(self, path, reload=None, widget=None, paths=None, **params):
        self.path = path
        self.path_x = paths
        self.reload = reload
        self.widget = boolean(widget)
        self.params = params

    @cached_property
    def params_reload(self):
        if self.widget:
            return {'reload': PARAM_WIDGETS_RELOAD.split('=')[1]}
        if self.reload == 'forced':
            return {'reload': PARAM_WIDGETS_RELOAD_FORCED.split('=')[1]}
        return {}

    @cached_property
    def params_widget(self):
        if not self.widget:
            return {}
        return {'widget': 'true'}

    @cached_property
    def params_path_x(self):
        if not self.path_x:
            return {}
        return {f'paths_{x}': i for x, i in enumerate(self.path_x) if i}

    @property
    def url(self):
        self.params.update(self.params_reload)
        self.params.update(self.params_widget)
        self.params.update(self.params_path_x)
        return encode_url(self.path, **self.params)


class _ListItem(object):

    mediatype = None
    trakt_type = None
    tmdb_type = None
    ftv_type = None
    playcount = None
    library = 'video'
    is_unaired = False

    context_additions = None
    infoproperties_additions = {}
    format_unaired_labels = False
    label_format_unaired = '{}'

    def __init__(
            self, label=None, label2=None, path=None, is_folder=True,
            params=None, next_page=None, context_menu=None,
            infolabels=None, infoproperties=None, art=None, cast=None,
            stream_details=None, unique_ids=None,
            **kwargs):

        self.label = label or ''
        self.label2 = label2 or ''
        self.path = path or PLUGINPATH
        self.is_folder = is_folder
        self.next_page = next_page

        self.infolabels = self.init_infolabels(infolabels)
        self.infoproperties = self.init_infoproperties(infoproperties)
        self.art = self.init_art(art)
        self.cast = self.init_cast(cast)
        self.context_menu = self.init_context_menu(context_menu)
        self.stream_details = self.init_stream_details(stream_details)
        self.unique_ids = self.init_unique_ids(unique_ids)
        self.params = self.init_params(params)

    @staticmethod
    def init_params(params):
        params = params or {}
        return params

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
    def is_resolvable(self):
        if self.is_folder:
            return False
        if self.params.get('info') != 'play':
            return False
        if global_setting['only_resolve_strm']:
            return False
        return True

    def finalise_infolabels(self):
        self.infolabels['path'] = self.url
        self.infolabels['playcount'] = self.playcount
        return self.infolabels

    def finalise_infoproperties(self):
        self.infoproperties.update({f'{k}_id': v for k, v in self.unique_ids.items() if v})  # Set UIDs to infoproperties
        self.infoproperties.update({f'item.{k}': v for k, v in self.params.items() if k and v})  # Set params to infoproperties
        self.infoproperties.update(self.infoproperties_additions)
        self.infoproperties.update({'isPlayable': 'true'}) if self.is_resolvable else None
        return self.infoproperties

    def finalise_context_menu(self):
        from tmdbhelper.lib.items.context import ContextMenu
        self.context_menu += ContextMenu(self).get()
        self.context_menu += self.context_additions or []
        return self.context_menu

    def finalise_art(self):
        self.art['icon'] = (
            self.art.get('icon')
            or self.art.get('poster')
            or self.art.get('thumb')
            or f'{ADDONPATH}/resources/icons/themoviedb/default.png'
        )
        return self.art

    def finalise_label(self):
        if self.format_unaired_labels and self.is_unaired:
            self.label = self.label_format_unaired.format(self.label)
        return self.label

    def finalise_params(self):
        if not self.path.startswith(PLUGINPATH):
            return self.params

        if global_setting['is_skinshortcuts']:
            self.finalise_params_skinshortcuts()

        if self.params.get('info') == 'details':
            return self.finalise_params_details()

        return self.params

    def finalise_params_details(self):
        return self.params

    def finalise_params_skinshortcuts(self):
        if not global_setting['is_skinshortcuts_standard']:
            self.params['widget'] = 'true'

        if self.infoproperties.get('is_sortable'):
            self.params['parent_info'] = self.params['info']
            self.params['info'] = 'mdblist_sortby' if self.infoproperties['is_sortable'] == 'mdblist' else 'trakt_sortby'  # Reroute sortable lists to display options in skinshortcuts

        if self.params.get('info') == 'search' and not self.params.get('query'):
            self.params['reload'] = 'forced'  # Add param to empty search to ensure reloads

    def finalise(self):
        self.finalise_params()
        self.finalise_infolabels()
        self.finalise_infoproperties()
        self.finalise_context_menu()
        self.finalise_art()
        self.finalise_label()
        return self

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

    @property
    def title(self):
        return self.label

    def set_details(self, details=None, reverse=False, override=False, reverse_artwork=False):
        if not details:
            return
        self.stream_details = merge_two_dicts(details.get('stream_details', {}), self.stream_details, reverse=reverse)
        self.infolabels = merge_two_dicts(details.get('infolabels', {}), self.infolabels, reverse=reverse)
        self.infoproperties = merge_two_dicts(details.get('infoproperties', {}), self.infoproperties, reverse=reverse)
        self.art = merge_two_dicts(details.get('art', {}), self.art, reverse=bool(reverse or reverse_artwork))
        self.unique_ids = merge_two_dicts(details.get('unique_ids', {}), self.unique_ids, reverse=reverse)
        self.cast = self.cast or details.get('cast', [])
        if not override:
            return
        self.label = details.get('label') or self.label
        self.infolabels['title'] = details.get('infolabels', {}).get('title') or self.infolabels.get('title')
        self.infolabels['tvshowtitle'] = details.get('infolabels', {}).get('tvshowtitle') or self.infolabels.get('tvshowtitle')

    @cached_property
    def url(self):
        return BuildURL(self.path, **self.params).url

    def get_listitem(self, offscreen=True, finalise=False):
        self.finalise() if finalise else None
        listitem = KodiListItem(label=self.label, label2=self.label2, path=self.url, offscreen=offscreen)
        return self.set_listitem(listitem)

    def set_infotag(self, listitem):
        info_tag = ListItemInfoTag(listitem)
        info_tag.set_info(self.infolabels)
        info_tag.set_unique_ids(self.unique_ids)
        info_tag.set_cast(self.cast)
        info_tag.set_stream_details(self.stream_details)
        info_tag.set_resume_point(self.infoproperties)
        return listitem

    def set_properties(self, listitem):
        listitem.setProperties({k: f'{v}' for k, v in self.infoproperties.items() if v not in (None, '')})
        return listitem

    def set_label2(self, listitem):
        listitem.setLabel2(self.label2)
        return listitem

    def set_art(self, listitem):
        listitem.setArt(self.art)
        return listitem

    def set_context_menu(self, listitem):
        listitem.addContextMenuItems(self.context_menu)
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
        self.params = self.init_params((kwargs.get('parent_params') or {}).copy())
        self.path = PLUGINPATH
        self.is_folder = True

    def finalise_infoproperties(self):
        super().finalise_infoproperties()
        self.infoproperties['specialsort'] = 'bottom'
        return self.infoproperties

    def finalise_art(self):
        self.art['icon'] = f'{ADDONPATH}/resources/icons/themoviedb/nextpage.png'
        self.art['landscape'] = f'{ADDONPATH}/resources/icons/themoviedb/nextpage_wide.png'
        return self.art

    def finalise_params(self):
        self.params['page'] = self.next_page
        self.params.pop('update_listing', None)  # Just in case we updated the listing for search results
        return self.params


class _Image(_ListItem):

    mediatype = 'image'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_folder = False

    def set_infotag(self, listitem):
        listitem.setInfo('pictures', {
            'title': self.label,
            'picturepath': self.url,
        })
        return listitem


class _Keyword(_ListItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_folder = True

    def finalise_params_details(self):
        self.params['info'] = 'discover'
        self.params['tmdb_type'] = 'movie'
        self.params['with_keywords'] = self.unique_ids.get('tmdb')
        self.params['with_id'] = 'True'
        return self.params


class _Studio(_ListItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_folder = True

    def finalise_params_details(self):
        self.params['info'] = 'discover'
        self.params['tmdb_type'] = 'movie'
        self.params['with_companies'] = self.unique_ids.get('tmdb')
        self.params['with_id'] = 'True'
        return self.params


class _Person(_ListItem):

    mediatype = 'video'  # Need to hack as video to allow info dialog
    tmdb_type = 'person'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_folder = True

    def finalise_params_details(self):
        self.params['info'] = 'credits_in_both'
        self.params['tmdb_type'] = 'person'
        self.params['tmdb_id'] = self.unique_ids.get('tmdb')
        return self.params


class _Collection(_ListItem):

    mediatype = 'set'
    tmdb_type = 'collection'

    def finalise_params_details(self):
        self.params['info'] = 'collection'
        return self.params


class _Video(_ListItem):

    mediatype = 'video'
    format_unaired_labels = True
    label_format_unaired = '[COLOR=ffcc0000][I]{}[/I][/COLOR]'

    @cached_property
    def is_unaired(self):
        return is_unaired_timestamp(self.infolabels.get('premiered'), True)

    def finalise_params_details(self):
        self.params['info'] = 'play'
        self.is_folder = False
        return self.params

    def finalise_context_menu(self):
        if not self.is_folder and self.params.get('info') == 'play':
            self.context_menu.insert(0, self.context_menu_selectplayer)
        return super().finalise_context_menu()

    @property
    def context_menu_selectplayer(self):
        head = '$ADDON[plugin.video.themoviedb.helper 32322]'
        path = f'RunPlugin({self.url}&ignore_default=true)'
        return (head, path)

    def get_context_menu_choosedefault_params(self):
        return [
            ('set_chosenplayer', self.title),
            ('tmdb_type', self.tmdb_type),
            ('tmdb_id', self.tmdb_id)
        ]

    @property
    def context_menu_choosedefault_paramstring(self):
        return ','.join([f'{k}={v}' for k, v in self.get_context_menu_choosedefault_params()])

    @property
    def context_menu_choosedefault(self):
        head = '$ADDON[plugin.video.themoviedb.helper 32476]'
        path = f'Runscript(plugin.video.themoviedb.helper,{self.context_menu_choosedefault_paramstring})'
        return (head, path)


class _Movie(_Video):

    mediatype = 'movie'
    trakt_type = 'movie'
    tmdb_type = 'movie'
    ftv_type = 'movies'

    @property
    def ftv_id(self):
        return self.unique_ids.get('tmdb')

    @property
    def playcount(self):
        return try_int(self.infolabels.get('playcount'), fallback=None)

    def finalise_context_menu(self):
        self.context_menu.append(self.context_menu_choosedefault)
        return super().finalise_context_menu()


class _Tvshow(_Video):

    mediatype = 'tvshow'
    trakt_type = 'show'
    tmdb_type = 'tv'
    ftv_type = 'tv'

    @property
    def ftv_id(self):
        return self.unique_ids.get('tvdb')

    @property
    def playcount(self):
        """
        For tvshows and seasons have to hardcode playcount as a 0|1 boolean
        because Kodi treats it as watched/unwatched boolean for whole show
        """
        if not self.totalepisodes:
            return 0
        if not self.watchedepisodes:
            return 0
        if self.totalepisodes > self.watchedepisodes:
            return 0
        return 1

    @property
    def totalepisodes(self):
        return try_int(self.infolabels.get('episode'), fallback=None)

    @property
    def totalseasons(self):
        return try_int(self.infolabels.get('season'), fallback=None)

    @property
    def watchedepisodes(self):
        if not self.totalepisodes:
            return
        return try_int(self.infoproperties.get('watchedepisodes'), fallback=0)

    @property
    def unwatchedepisodes(self):
        if self.watchedepisodes is None:
            return
        return self.totalepisodes - self.watchedepisodes

    @property
    def watchedprogress(self):
        if not self.totalepisodes:
            return
        if self.watchedepisodes is None:
            return
        return int(self.watchedepisodes * 100 / self.totalepisodes)

    def finalise_infoproperties(self):
        super().finalise_infoproperties()
        self.infoproperties['totalepisodes'] = self.totalepisodes
        self.infoproperties['watchedepisodes'] = self.watchedepisodes
        self.infoproperties['unwatchedepisodes'] = self.unwatchedepisodes
        self.infoproperties['watchedprogress'] = self.watchedprogress
        self.infoproperties['totalseasons'] = self.totalseasons
        return self.infoproperties

    def finalise_params_details(self):
        self.params['info'] = global_setting['flatseasons_info_param']
        return self.params

    def finalise_context_menu(self):
        self.context_menu.append(self.context_menu_choosedefault)
        return super().finalise_context_menu()


class _Season(_Tvshow):

    mediatype = 'season'
    trakt_type = 'season'

    def finalise_infoproperties(self):
        super(_Tvshow, self).finalise_infoproperties()  # Skip TV Show additions
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

    def get_context_menu_choosedefault_params(self):
        params = super().get_context_menu_choosedefault_params()
        params.extend([
            ('season', self.season)
        ])
        return params

    def finalise_params_details(self):
        self.params['info'] = 'episodes'
        return self.params


class _Episode(_Video):

    mediatype = 'episode'
    trakt_type = 'episode'
    tmdb_type = 'tv'
    ftv_type = 'tv'
    thumb_override = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_format = self.init_label_format()

    def init_label_format(self):
        if boolean(self.infoproperties.pop('no_label_formatting', False)):
            return '{label}'
        if not self.episode or self.season is None:
            return '{label}'
        return '{season}x{episode:0>2}. {label}'

    @property
    def playcount(self):
        return try_int(self.infolabels.get('playcount'), fallback=None)

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

    def finalise_art(self):
        self.art = super().finalise_art()
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
    def title(self):
        return self.infolabels.get('title') or self.label

    def finalise_label(self):
        self.label = self.label_format.format(season=self.season, episode=self.episode, label=self.title)
        self.label = super().finalise_label()
        return self.label

    def get_context_menu_choosedefault_params(self):
        params = super().get_context_menu_choosedefault_params()
        params.extend([
            ('season', self.season),
            ('episode', self.episode)
        ])
        return params

    def finalise_context_menu(self):
        self.context_menu.append(self.context_menu_choosedefault)
        return super().finalise_context_menu()

        # if (self.parent_params.get('info') == 'library_nextaired'
        #         and global_setting['nextaired_linklibrary']
        #         and self.infoproperties.get('tvshow.dbid')):
        #     self.path = f'videodb://tvshows/titles/{self.infoproperties["tvshow.dbid"]}/'
        #     self.params = {}
        #     self.is_folder = True
        #     return
