from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from jurialmunkey.parser import try_int


class PlayerActionDialogFolderItemJSONRPCStreamDetails:
    method = None
    key = None

    def __init__(self, dbid):
        self.dbid = dbid

    @cached_property
    def params(self):
        return {
            "properties": ["streamdetails"],
            self.params_key: int(self.dbid)
        }

    @cached_property
    def streamdetails(self):
        if not self.dbid:
            return
        from tmdbhelper.lib.api.kodi.rpc import get_jsonrpc
        try:
            jsonrpc_streamdetails = get_jsonrpc(self.method, self.params)
            return jsonrpc_streamdetails['result'][self.result_key]['streamdetails']
        except (KeyError, AttributeError, TypeError, IndexError):
            return


class PlayerActionDialogFolderItemJSONRPCStreamDetailsMovie(PlayerActionDialogFolderItemJSONRPCStreamDetails):
    method = "VideoLibrary.GetMovieDetails"
    params_key = "movieid"
    result_key = "moviedetails"


class PlayerActionDialogFolderItemJSONRPCStreamDetailsEpisode(PlayerActionDialogFolderItemJSONRPCStreamDetails):
    method = "VideoLibrary.GetEpisodeDetails"
    params_key = "episodeid"
    result_key = "episodedetails"


class PlayerActionDialogFolderItem:
    def __init__(self, meta):
        self.meta = meta

    @staticmethod
    def get_object_key(obj, key):
        try:
            return obj[key]
        except (KeyError, AttributeError, TypeError, IndexError):
            return

    @cached_property
    def is_visible(self):
        return bool(self.main_label and self.main_label != 'None')

    @cached_property
    def file(self):
        return self.get_object_key(self.meta, 'file')

    @cached_property
    def mediatype(self):
        return self.get_object_key(self.meta, 'type')

    @cached_property
    def dbid(self):
        return self.get_object_key(self.meta, 'id')

    @cached_property
    def year(self):
        year = self.get_object_key(self.meta, 'year')
        year = None if year == 1601 else year
        return year

    @cached_property
    def episode(self):
        episode = self.get_object_key(self.meta, 'episode')
        episode = try_int(episode, fallback=None) or None
        episode = episode if episode and episode != -1 else None
        return episode

    @cached_property
    def season(self):
        if not self.episode:
            return
        season = self.get_object_key(self.meta, 'season')
        season = try_int(season, fallback=None) or None
        season = season if season and season != -1 else None
        return season

    @cached_property
    def filetype(self):
        return self.get_object_key(self.meta, 'filetype')

    @cached_property
    def is_folder(self):
        return bool(self.filetype != 'file')

    @cached_property
    def filesize(self):
        from tmdbhelper.lib.files.futils import normalise_filesize
        filesize = self.get_object_key(self.meta, 'size')
        filesize = normalise_filesize(filesize) if filesize else None
        return filesize

    @cached_property
    def jsonrpc_streamdetails(self):
        if not self.dbid:
            return
        routes = {
            'movie': PlayerActionDialogFolderItemJSONRPCStreamDetailsMovie,
            'episode': PlayerActionDialogFolderItemJSONRPCStreamDetailsEpisode,
        }
        try:
            return routes[self.mediatype](self.dbid).streamdetails
        except (KeyError, AttributeError, TypeError, IndexError):
            return

    @cached_property
    def streamdetails(self):
        return self.get_object_key(self.meta, 'streamdetails')

    @cached_property
    def streamdetails_video(self):
        streamdetails_video = self.get_object_key(self.streamdetails, 'video')
        streamdetails_video = streamdetails_video or self.get_object_key(self.jsonrpc_streamdetails, 'video')
        return streamdetails_video

    @cached_property
    def streamdetails_video_main(self):
        return self.get_object_key(self.streamdetails_video, 0)

    @cached_property
    def streamdetails_audio(self):
        streamdetails_audio = self.get_object_key(self.streamdetails, 'audio')
        streamdetails_audio = streamdetails_audio or self.get_object_key(self.jsonrpc_streamdetails, 'audio')
        return streamdetails_audio

    @cached_property
    def streamdetails_audio_main(self):
        return self.get_object_key(self.streamdetails_audio, 0)

    @cached_property
    def episode_count(self):
        if not self.season or not self.is_folder:
            return
        return f'{self.episode} {get_localized(20360)}'

    @cached_property
    def video_width(self):
        return self.get_object_key(self.streamdetails_video_main, 'width')

    @cached_property
    def video_height(self):
        return self.get_object_key(self.streamdetails_video_main, 'height')

    @cached_property
    def video_resolution(self):
        if not self.video_width or not self.video_height:
            return
        return f'{self.video_width}x{self.video_height}'

    @cached_property
    def video_codec(self):
        video_codec = self.get_object_key(self.streamdetails_video_main, 'codec') or ''
        video_codec = video_codec.upper()
        return video_codec

    @cached_property
    def video_duration(self):
        video_duration = self.get_object_key(self.streamdetails_video_main, 'duration')
        video_duration = f'{try_int(video_duration) // 60} mins' if video_duration else None
        return video_duration

    @cached_property
    def audio_codec(self):
        audio_codec = self.get_object_key(self.streamdetails_audio_main, 'codec') or ''
        audio_codec = audio_codec.upper()
        return audio_codec

    @cached_property
    def audio_channels(self):
        audio_channels = self.get_object_key(self.streamdetails_audio_main, 'channels')
        audio_channels = f'{audio_channels} CH' if audio_channels else None
        return audio_channels

    @cached_property
    def audio_languages(self):
        return [
            self.get_object_key(i, 'language').upper()
            for i in (self.streamdetails_audio or ())
            if self.get_object_key(i, 'language')
        ]

    @cached_property
    def main_label(self):
        main_label = self.get_object_key(self.meta, 'title')
        main_label = main_label or self.get_object_key(self.meta, 'label')
        return main_label

    @cached_property
    def year_suffix(self):
        if not self.year:
            return
        return f'({self.year})'

    @cached_property
    def episode_prefix(self):
        if not self.season or self.is_folder:
            return
        return f'{self.season}x{self.episode}.'

    @cached_property
    def label(self):
        return ' '.join(self.label_joinlist)

    @cached_property
    def label2(self):
        return ' | '.join(self.label2_joinlist)

    @cached_property
    def label_joinlist(self):
        return [
            i for i in (
                self.episode_prefix,
                self.main_label,
                self.year_suffix,
            ) if i]

    @cached_property
    def label2_joinlist(self):
        label2_joinlist = [
            i for i in (
                self.episode_count,
                self.video_resolution,
                self.video_codec,
                self.audio_codec,
                self.audio_channels,
            ) if i]
        label2_joinlist += self.audio_languages
        label2_joinlist += [
            i for i in (
                self.video_duration,
                self.filesize,
            ) if i]
        return label2_joinlist

    @cached_property
    def art(self):
        return {'thumb': self.get_object_key(self.meta, 'thumbnail')}

    @cached_property
    def item(self):
        return {
            'label': self.label,
            'label2': self.label2,
            'art': self.art,
        }

    @cached_property
    def listitem(self):
        from tmdbhelper.lib.items.listitem import ListItem
        return ListItem(**self.item).get_listitem()


class PlayerActionDialog:
    def __init__(self, folder):
        self.folder = folder

    @cached_property
    def folder_items(self):
        return [
            i for i in (
                PlayerActionDialogFolderItem(f)
                for f in self.folder
            ) if i.is_visible
        ]

    @cached_property
    def folder_listitems(self):
        return [f.listitem for f in self.folder_items]

    @cached_property
    def choice(self):
        if not self.folder_items:
            return -1
        from xbmcgui import Dialog
        return Dialog().select(get_localized(32236), self.folder_listitems, useDetails=True)

    @cached_property
    def item(self):
        if self.choice == -1:
            return
        return self.folder_items[self.choice]

    @cached_property
    def item_tuple(self):
        if not self.item:
            return
        return (self.item.file, self.item.is_folder)
