from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList


class VideoMediaList(MediaList):
    cached_data_table = table = 'video'
    cached_data_base_conditions = 'parent_id=?'
    cached_data_check_key = 'parent_id'
    keys = ('name', 'iso_language', 'iso_country', 'key', 'release_date as premiered', 'path', 'content', 'parent_id')
    item_mediatype = 'video'
    item_tmdb_type = 'video'
    item_label_key = 'name'
    item_alter_key = ''

    order_by = 'content="Trailer" DESC'

    @property
    def cached_data_values(self):
        return (self.item_id, )

    @staticmethod
    def map_item_unique_ids(i):
        return {}

    @staticmethod
    def map_item_params(i):
        return {}

    @staticmethod
    def map_item_art(i):
        return {'thumb': f'https://img.youtube.com/vi/{i["key"]}/0.jpg'}

    def map_item(self, i):
        item = super().map_item(i)
        item['path'] = i['path']
        item['infoproperties']['isPlayable'] = True
        item['is_folder'] = False
        return item


class Movie(VideoMediaList):
    pass


class Tvshow(VideoMediaList):
    pass


class Season(VideoMediaList):
    pass


class Episode(VideoMediaList):
    pass


class Person(VideoMediaList):
    pass
