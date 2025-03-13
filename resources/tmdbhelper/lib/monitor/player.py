from xbmc import Player
from jurialmunkey.parser import boolean
from jurialmunkey.window import get_property
from tmdbhelper.lib.monitor.images import ImageFunctions
from tmdbhelper.lib.monitor.common import CommonMonitorFunctions, SETPROP_RATINGS, SETMAIN_ARTWORK
from tmdbhelper.lib.addon.plugin import get_condvisibility, get_infolabel


class PlayerTMDbItem():
    def __init__(self, parent):
        self._parent = parent

    @property
    def baseitem(self):
        try:
            return self._baseitem
        except AttributeError:
            self._baseitem = self.get_baseitem()
            return self._baseitem

    def get_baseitem(self):
        if not self._parent.isPlayingVideo():
            return
        return self._parent.ib.get_item(
            self._parent.tmdb_type,
            self._parent.tmdb_id,
            self._parent.season,
            self._parent.episode)

    @property
    def details(self):
        try:
            return self._details
        except AttributeError:
            self._details = self.get_baseitem_details()
            return self._details

    def get_baseitem_details(self):
        if not self.baseitem:
            return {}
        return self.baseitem['listitem']

    @property
    def artwork(self):
        try:
            return self._artwork
        except AttributeError:
            self._artwork = self.get_baseitem_artwork()
            return self._artwork

    def get_baseitem_artwork(self):
        if not self.baseitem:
            return {}
        return self.baseitem['artwork']

    @property
    def info_tag(self):
        try:
            return self._info_tag
        except AttributeError:
            self._info_tag = self.get_info_tag()
            return self._info_tag

    def get_info_tag(self):
        if self._parent.isPlayingVideo():
            return self._parent.getVideoInfoTag()
        if self._parent.isPlayingAudio():
            return self._parent.getMusicInfoTag()

    @property
    def dbtype(self):
        try:
            return self._dbtype
        except AttributeError:
            self._dbtype = self.info_tag.getMediaType()
            return self._dbtype

    @property
    def dbid(self):
        try:
            return self._dbid
        except AttributeError:
            self._dbid = self.info_tag.getDbId()
            return self._dbid

    @property
    def imdb_id(self):
        if self.dbtype == 'movie':
            return self.info_tag.getIMDBNumber()

    @property
    def query(self):
        if self.dbtype == 'episode':
            return self.info_tag.getTVShowTitle()
        return self.info_tag.getTitle()

    @property
    def year(self):
        if self.dbtype == 'episode':
            return
        return self.info_tag.getYear()

    @property
    def epyear(self):
        if self.dbtype == 'episode':
            self.info_tag.getYear()

    @property
    def season(self):
        if self.dbtype == 'episode':
            return self.info_tag.getSeason()

    @property
    def episode(self):
        if self.dbtype == 'episode':
            return self.info_tag.getEpisode()

    @property
    def tmdb_type(self):
        if self.dbtype == 'movie':
            return 'movie'
        if self.dbtype == 'episode':
            return 'tv'
        return ''

    @property
    def tmdb_id(self):
        try:
            return self._tmdb_id
        except AttributeError:
            self._tmdb_id = self.get_tmdb_id()
            return self._tmdb_id

    def get_tmdb_id(self):
        if self.dbtype not in ('episode', 'movie'):
            return

        if self.dbtype == 'episode':
            tmdb_id = self.info_tag.getUniqueID('tvshow.tmdb')
            tmdb_id = tmdb_id or self._parent.get_tmdb_id_parent(
                self.info_tag.getUniqueID('tmdb'), 'episode',
                season_episode_check=(self.season, self.episode,))
        else:
            tmdb_id = self.info_tag.getUniqueID('tmdb')

        return tmdb_id or self._parent.get_tmdb_id(
            self.tmdb_type,
            self.imdb_id,
            self.query,
            self.year,
            self.epyear)

    def get_ratings(self):
        if not self.details:
            return {}
        if get_condvisibility("Skin.HasSetting(TMDbHelper.DisableRatings)"):
            return {}
        try:
            trakt_type = {'movie': 'movie', 'tv': 'show'}[self.tmdb_type]
        except KeyError:
            trakt_type = None
        if not trakt_type:
            return {}
        details = self.details
        details = self._parent.get_omdb_ratings(details)
        details = self._parent.get_imdb_top250_rank(details, trakt_type=trakt_type)
        details = self._parent.get_tvdb_awards(details, self.tmdb_type, self.tmdb_id)
        details = self._parent.get_trakt_ratings(details, trakt_type, season=self.season, episode=self.episode)
        details = self._parent.get_mdblist_ratings(details, trakt_type, tmdb_id=self.tmdb_id)
        return details.get('infoproperties', {})

    def get_artwork(self):
        if get_condvisibility("Skin.HasSetting(TMDbHelper.DisableArtwork)"):
            return {}
        if not self.artwork:
            return {}
        self.details['art'] = self._parent.ib.get_item_artwork(self.artwork, is_season=True if self.season else False)
        return self.details['art']


class PlayerMonitor(Player, CommonMonitorFunctions):
    def __init__(self):
        Player.__init__(self)
        CommonMonitorFunctions.__init__(self)
        self.playerstring = None
        self.property_prefix = 'Player'
        self.reset_properties()

    def onAVStarted(self):
        self.reset_properties()
        self.get_playingitem()

    def onAVChange(self):
        self.reset_properties()
        self.get_playingitem()

    def onPlayBackEnded(self):
        self.set_watched()
        self.reset_properties()
        self.update_trakt()

    def onPlayBackStopped(self):
        self.set_watched()
        self.reset_properties()
        self.update_trakt()

    def reset_properties(self):
        self.clear_properties()
        self.clear_artwork()
        self.total_time = 0
        self.current_time = 0
        self.previous_item = None
        self.current_item = None
        self.player_item = PlayerTMDbItem(self)

    @property
    def details(self):
        return self.player_item.details

    @property
    def artwork(self):
        return self.player_item.artwork

    @property
    def info_tag(self):
        return self.player_item.info_tag

    @property
    def dbtype(self):
        return self.player_item.dbtype

    @property
    def dbid(self):
        return self.player_item.dbid

    @property
    def imdb_id(self):
        return self.player_item.imdb_id

    @property
    def query(self):
        return self.player_item.query

    @property
    def year(self):
        return self.player_item.year

    @property
    def epyear(self):
        return self.player_item.epyear

    @property
    def season(self):
        return self.player_item.season

    @property
    def episode(self):
        return self.player_item.episode

    @property
    def tmdb_type(self):
        return self.player_item.tmdb_type

    @property
    def tmdb_id(self):
        return self.player_item.tmdb_id

    def update_trakt(self):
        if not boolean(get_property('TraktIsAuth')):
            return
        from tmdbhelper.lib.script.method.trakt import get_stats
        from tmdbhelper.lib.api.trakt.methods.activities import del_lastactivities_expiry
        del_lastactivities_expiry()
        get_stats()

    def update_time(self):
        self.current_time = self.getTime()

    def update_crop(self):
        if get_condvisibility("!Skin.HasSetting(TMDbHelper.EnableCrop)"):
            return

        art = self.details.get('art') or {}

        clearlogo = (
            get_infolabel('Player.Art(clearlogo)')
            or get_infolabel('Player.Art(artist.clearlogo)')
            or get_infolabel('Player.Art(tvshow.clearlogo)')
            or art.get('clearlogo')
            or art.get('tvshow.clearlogo'))

        if clearlogo != self.previous_clearlogo:
            ImageFunctions(method='crop', is_thread=False, prefix='Player', artwork=clearlogo).run()
            self.previous_clearlogo = clearlogo

    def update_blur(self):
        if get_condvisibility("!Skin.HasSetting(TMDbHelper.EnableBlur)"):
            return

        art = self.details.get('art') or {}

        fanart = (
            get_infolabel('Player.Art(fanart)')
            or get_infolabel('Player.Art(artist.fanart)')
            or get_infolabel('Player.Art(tvshow.fanart)')
            or art.get('fanart')
            or art.get('tvshow.fanart'))

        poster = (
            get_infolabel('Player.Art(poster)')
            or get_infolabel('Player.Art(artist.poster)')
            or get_infolabel('Player.Art(tvshow.poster)')
            or get_infolabel('Player.Icon')
            or art.get('poster')
            or art.get('tvshow.poster'))

        if poster != self.previous_poster:
            ImageFunctions(method='blur', is_thread=False, prefix='Player.Poster', artwork=poster).run()
            self.previous_poster = poster

        if fanart != self.previous_fanart:
            ImageFunctions(method='blur', is_thread=False, prefix='Player.Fanart', artwork=fanart).run()
            self.previous_fanart = fanart

    def update_artwork(self):
        self.update_crop()
        self.update_blur()

    def clear_artwork(self):
        self.clear_property('CropImage')
        self.clear_property('CropImage.Original')
        self.clear_property('Poster.BlurImage')
        self.clear_property('Poster.BlurImage.Original')
        self.clear_property('Fanart.BlurImage')
        self.clear_property('Fanart.BlurImage.Original')
        self.previous_clearlogo = None
        self.previous_poster = None
        self.previous_fanart = None

    def get_playingitem(self):
        # Check that video other than dummy splash video is playing
        if self.getPlayingFile() and self.getPlayingFile().endswith('dummy.mp4'):
            self.reset_properties()
            return

        # Update some base values
        from json import loads
        self.playerstring = get_property('PlayerInfoString')
        self.playerstring = loads(self.playerstring) if self.playerstring else None
        self.total_time = self.getTotalTime()

        self.current_item = (
            self.total_time,
            self.dbtype,
            self.dbid,
            self.imdb_id,
            self.query,
            self.year,
            self.epyear,
            self.season,
            self.episode,
        )

        # Avoid resetting the same item
        if self.previous_item and self.current_item == self.previous_item:
            return

        # Clear properties and store the last cleared item
        self.previous_item = self.current_item
        self.clear_properties()
        self.clear_artwork()

        # Only get info for Movies and Episodes -- TODO: Maybe get for PVR details?
        if self.dbtype not in ('movie', 'episode', ):
            self.update_artwork()
            return

        # Get ratings and artwork (no need for threading since we're only getting one item in player ever)
        self.set_iter_properties(self.player_item.get_ratings(), SETPROP_RATINGS)
        self.set_iter_properties(self.player_item.get_artwork(), SETMAIN_ARTWORK)

        # Update our properties
        self.set_properties(self.details)

        # Update our artwork manipulation cropped logo
        self.update_artwork()

    def set_watched(self):
        if not self.playerstring:
            return
        if not self.playerstring.get('tmdb_id'):
            return
        if not self.current_time:
            return
        if not self.total_time:
            return

        # Item in the player doesn't match so don't mark as watched
        if f'{self.playerstring.get("tmdb_id")}' != f'{self.details.get("unique_ids", {}).get("tmdb")}':
            return

        # Only update if progress is 75% or more
        if ((self.current_time / self.total_time) * 100) < 75:
            return

        import tmdbhelper.lib.api.kodi.rpc as rpc

        if self.playerstring.get('tmdb_type') == 'episode':
            tvshowid = rpc.KodiLibrary('tvshow').get_info(
                info='dbid',
                imdb_id=self.playerstring.get('imdb_id'),
                tmdb_id=self.playerstring.get('tmdb_id'),
                tvdb_id=self.playerstring.get('tvdb_id'))
            if not tvshowid:
                return
            dbid = rpc.KodiLibrary('episode', tvshowid).get_info(
                info='dbid',
                season=self.playerstring.get('season'),
                episode=self.playerstring.get('episode'))
            if not dbid:
                return
            rpc.set_watched(dbid=dbid, dbtype='episode')
            return

        if self.playerstring.get('tmdb_type') == 'movie':
            dbid = rpc.KodiLibrary('movie').get_info(
                info='dbid',
                imdb_id=self.playerstring.get('imdb_id'),
                tmdb_id=self.playerstring.get('tmdb_id'),
                tvdb_id=self.playerstring.get('tvdb_id'))
            if not dbid:
                return
            rpc.set_watched(dbid=dbid, dbtype='movie')
            return
