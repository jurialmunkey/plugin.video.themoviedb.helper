from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import merge_two_items


class BaseDirDetailsItemBuilder:

    mediatype = None

    def __init__(self, base_item, tmdb_type, tmdb_id, detailed_item=None, **kwargs):
        self.base_item = base_item  # BaseDirItem
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.detailed_item = detailed_item or {}

    @cached_property
    def context_menu(self):
        context_menu = []
        return context_menu

    @cached_property
    def infolabels(self):
        infolabels = {
            'title': self.label,
            'mediatype': self.mediatype,
        }
        infolabels.update(self.base_item.infolabels)
        return infolabels

    @cached_property
    def infoproperties(self):
        infoproperties = {}
        infoproperties.update(self.base_item.infoproperties)
        return infoproperties

    @cached_property
    def item_params(self):
        return {
            'info': 'details',
            'tmdb_id': self.tmdb_id,
            'tmdb_type': self.tmdb_type,
        }

    @cached_property
    def params(self):
        params = self.item_params
        params.update(self.base_item.params)
        return params

    @cached_property
    def art(self):
        art = {}
        art.update(self.base_item.art)
        return art

    @cached_property
    def label(self):
        return self.base_item.label

    @cached_property
    def item(self):
        item = {
            'label': self.label,
            'params': self.params,
            'infolabels': self.infolabels,
            'infoproperties': self.infoproperties,
            'context_menu': self.context_menu,
            'art': self.art,
        }
        return merge_two_items(self.detailed_item, item)


class BaseDirDetailsItemBuilderMovie(BaseDirDetailsItemBuilder):
    mediatype = 'movie'


class BaseDirDetailsItemBuilderTVShow(BaseDirDetailsItemBuilder):
    mediatype = 'tvshow'


class BaseDirDetailsItemBuilderSeason(BaseDirDetailsItemBuilder):
    mediatype = 'season'

    def __init__(self, base_item, tmdb_type, tmdb_id, season=None, detailed_item=None, **kwargs):
        self.base_item = base_item  # BaseDirItem
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.detailed_item = detailed_item or {}

    @cached_property
    def item_params(self):
        return {
            'info': 'details',
            'tmdb_id': self.tmdb_id,
            'tmdb_type': self.tmdb_type,
            'season': self.season,
        }


class BaseDirDetailsItemBuilderEpisode(BaseDirDetailsItemBuilder):
    mediatype = 'episode'

    def __init__(self, base_item, tmdb_type, tmdb_id, season=None, episode=None, detailed_item=None, **kwargs):
        self.base_item = base_item  # BaseDirItem
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.detailed_item = detailed_item or {}

    @cached_property
    def item_params(self):
        return {
            'info': 'details',
            'tmdb_id': self.tmdb_id,
            'tmdb_type': self.tmdb_type,
            'season': self.season,
            'episode': self.episode,
        }


class BaseDirDetailsItemBuilderPerson(BaseDirDetailsItemBuilder):
    mediatype = 'person'


def configure(instance, tmdb_type, tmdb_id, season=None, episode=None, detailed_item=None, **kwargs):

    def class_object():
        if tmdb_type == 'movie':
            return BaseDirDetailsItemBuilderMovie
        if tmdb_type == 'tv' and season is not None and episode is not None:
            return BaseDirDetailsItemBuilderEpisode
        if tmdb_type == 'tv' and season is not None:
            return BaseDirDetailsItemBuilderSeason
        if tmdb_type == 'tv':
            return BaseDirDetailsItemBuilderTVShow
        if tmdb_type == 'person':
            return BaseDirDetailsItemBuilderPerson

    instance = instance()
    instance.item_builder = class_object()(
        instance,
        tmdb_type=tmdb_type,
        tmdb_id=tmdb_id,
        season=season,
        episode=episode,
        detailed_item=detailed_item,
    )
    instance.get_item = lambda *discarded_args, **discarded_kwgs: instance.item_builder.item
    return instance
