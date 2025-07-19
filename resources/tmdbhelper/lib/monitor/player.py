from xbmc import Player
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.monitor.images import ImageFunctions
from tmdbhelper.lib.monitor.common import CommonMonitorFunctions
from tmdbhelper.lib.addon.plugin import get_condvisibility, get_infolabel, get_setting
from tmdbhelper.lib.monitor.scrobbler import PlayerScrobbler


class PlayerItem():
    def __init__(self, parent):
        self._parent = parent

    @cached_property
    def baseitem(self):
        if not self._parent.isPlayingVideo():
            return
        item_data = self._parent.lidc.get_item(
            self._parent.tmdb_type,
            self._parent.tmdb_id,
            self._parent.season,
            self._parent.episode)

        try:
            return {
                'listitem': item_data,
                'artwork': item_data['art'],
            }
        except (KeyError, AttributeError, TypeError):
            return {}

    @cached_property
    def details(self):
        if not self.baseitem:
            return {}
        return self.baseitem['listitem']

    @cached_property
    def artwork(self):
        if not self.baseitem:
            return {}
        return self.baseitem['artwork']

    @cached_property
    def meta(self):
        info_tag = self.get_player_info_tag()

        if not info_tag:
            return {}

        meta = {}
        meta['DbId'] = info_tag.getDbId()
        meta['MediaType'] = info_tag.getMediaType()
        meta['Title'] = info_tag.getTitle()
        meta['Year'] = info_tag.getYear()

        if self._parent.isPlayingVideo():
            meta['IMDBNumber'] = info_tag.getIMDBNumber()
            meta['TVShowTitle'] = info_tag.getTVShowTitle()
            meta['Season'] = info_tag.getSeason()
            meta['Episode'] = info_tag.getEpisode()
            meta['UniqueID.tvshow.tmdb'] = info_tag.getUniqueID('tvshow.tmdb')
            meta['UniqueID.tmdb'] = info_tag.getUniqueID('tmdb')

        return meta

    def get_player_info_tag(self):
        if self._parent.isPlayingVideo():
            return self._parent.getVideoInfoTag()
        if self._parent.isPlayingAudio():
            return self._parent.getMusicInfoTag()

    @property
    def dbtype(self):
        return self.meta.get('MediaType')

    @property
    def dbid(self):
        return self.meta.get('DbId')

    @property
    def imdb_id(self):
        return self.meta.get('IMDBNumber')

    @property
    def query(self):
        if self.dbtype == 'episode':
            return self.meta.get('TVShowTitle')
        return self.meta.get('Title')

    @property
    def year(self):
        if self.dbtype == 'episode':
            return
        return self.meta.get('Year')

    @property
    def episode_year(self):
        if self.dbtype != 'episode':
            return
        return self.meta.get('Year')

    @property
    def season(self):
        if self.dbtype != 'episode':
            return
        return self.meta.get('Season')

    @property
    def episode(self):
        if self.dbtype != 'episode':
            return
        return self.meta.get('Episode')

    @property
    def tmdb_type(self):
        if self.dbtype == 'movie':
            return 'movie'
        if self.dbtype == 'episode':
            return 'tv'
        return ''

    @property
    def infolabel_uniqueid_tmdb(self):
        return self.meta.get('UniqueID.tmdb')

    @property
    def infolabel_uniqueid_tvshow_tmdb(self):
        return self.meta.get('UniqueID.tvshow.tmdb')

    @cached_property
    def identifier_id(self):
        from tmdbhelper.lib.query.database.identifier import make_identifier_id
        return make_identifier_id(
            dbtype=f'{self.dbtype}s' if self.dbtype else None,
            query=self.query,
            season=self.season,
            episode=self.episode,
            imdb_id=self.imdb_id,
            year=self.year,
            episode_year=self.episode_year,
            infolabel_uniqueid_tmdb=self.infolabel_uniqueid_tmdb,
            infolabel_uniqueid_tvshow_tmdb=self.infolabel_uniqueid_tvshow_tmdb,
        )

    @cached_property
    def tmdb_id(self):
        identifier_details = self._parent.get_identifier_details(self.identifier_id)
        identifier_details = identifier_details or self._parent.set_identifier_details(
            self.identifier_id,
            self.get_tmdb_id(),
            self.tmdb_type
        )
        if identifier_details:
            # self.tmdb_type = identifier_details.tmdb_type  # TODO: Check if we need this in player like service
            return identifier_details.tmdb_id

    def get_tmdb_id_parent(self):
        if self.dbtype == 'episode':
            return self.infolabel_uniqueid_tvshow_tmdb or self._parent.get_tmdb_id_parent(
                tmdb_id=self.infolabel_uniqueid_tmdb,
                item_type='episode',
                season=self.season,
                episode=self.episode,
            )
        return self.infolabel_uniqueid_tmdb

    def get_tmdb_id(self):
        if self.dbtype in ('episode', 'movie'):
            return self.get_tmdb_id_parent() or self._parent.get_tmdb_id(
                tmdb_type=self.tmdb_type,
                query=self.query,
                imdb_id=self.imdb_id,
                year=self.year,
                episode_year=self.episode_year,
            )

    def get_ratings(self):
        if not self.details:
            return {}
        if get_condvisibility("Skin.HasSetting(TMDbHelper.DisableRatings)"):
            return {}
        return self._parent.get_all_ratings(self.tmdb_type, self.tmdb_id, self.season, self.episode) or {}


class PlayerMonitor(Player, CommonMonitorFunctions):
    def __init__(self):
        Player.__init__(self)
        CommonMonitorFunctions.__init__(self)
        self.property_prefix = 'Player'
        self.reset_properties()

    def onAVStarted(self):
        self.get_playingitem()

    def onAVChange(self):
        self.get_playingitem()

    def onPlayBackEnded(self):
        self.scrobbler_stop()
        self.reset_properties()

    def onPlayBackStopped(self):
        self.scrobbler_stop()
        self.reset_properties()

    def onPlayBackPaused(self):
        self.scrobbler_pause()

    def onPlayBackResumed(self):
        self.scrobbler_start()

    def reset_player_item(self):
        self.player_item = PlayerItem(self)

    def reset_properties(self):
        self.clear_properties()
        self.clear_artwork()
        self.previous_item = None
        self.current_item = None
        self.playerstring = None
        self.scrobbler = None

    def scrobbler_start(self):
        if not self.scrobbler:
            return
        self.scrobbler.start(self.tmdb_type, self.tmdb_id)

    def scrobbler_pause(self):
        if not self.scrobbler:
            return
        self.scrobbler.pause(self.tmdb_type, self.tmdb_id)

    def scrobbler_stop(self):
        if not self.scrobbler:
            return
        self.scrobbler.stop(self.tmdb_type, self.tmdb_id)

    def update_time(self):
        if not self.scrobbler:
            return
        self.scrobbler.update_time(self.tmdb_type, self.tmdb_id, self.getTime())

    @cached_property
    def player_item(self):
        return PlayerItem(self)

    @property
    def details(self):
        return self.player_item.details

    @property
    def artwork(self):
        return self.player_item.artwork

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

    def get_clearlogo(self):
        art = self.details.get('art') or {}
        return (
            (
                art.get('clearlogo')
                or art.get('tvshow.clearlogo')
                or get_infolabel('Player.Art(clearlogo)')
                or get_infolabel('Player.Art(artist.clearlogo)')
                or get_infolabel('Player.Art(tvshow.clearlogo)')
            )
            if get_setting('service_prefers_online_clearlogo') else
            (
                get_infolabel('Player.Art(clearlogo)')
                or get_infolabel('Player.Art(artist.clearlogo)')
                or get_infolabel('Player.Art(tvshow.clearlogo)')
                or art.get('clearlogo')
                or art.get('tvshow.clearlogo')
            )

        )

    def update_crop(self):
        if get_condvisibility("!Skin.HasSetting(TMDbHelper.EnableCrop)"):
            return

        clearlogo = self.get_clearlogo()

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

        # Get fresh info tags etc.
        self.reset_player_item()
        self.current_item = (
            self.dbtype,
            self.dbid,
            self.imdb_id,
            self.query,
            self.year,
            self.season,
            self.episode,
        )

        # Avoid resetting the same item
        if self.previous_item and self.current_item == self.previous_item:
            return

        # Update scrobbler
        self.scrobbler_stop()
        self.scrobbler = PlayerScrobbler(trakt_api=self.trakt_api, total_time=self.getTotalTime())

        # Clear properties and store the last cleared item
        self.previous_item = self.current_item
        self.clear_properties()

        # Extra info only for Movies and Episodes. Exit early and only update monitor art for other types. TODO: Maybe get extra PVR info?
        if self.dbtype not in ('movie', 'episode', ):
            self.update_artwork()
            return

        # Update our artwork manipulation cropped logo
        self.update_artwork()

        # Update ratings
        self.set_ratings_properties({'ratings': self.player_item.get_ratings()})

        # Update our properties
        self.set_properties(self.details)

        # Start Trakt trakt_scrobbling
        self.scrobbler_start()
