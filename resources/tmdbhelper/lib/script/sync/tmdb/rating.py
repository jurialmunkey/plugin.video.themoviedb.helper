from tmdbhelper.lib.script.sync.tmdb.item import ItemSync
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator


class ItemRating(ItemSync):
    localized_name_add = 32485
    localized_name_rem = 32530
    tmdb_list_type = 'rating'
    convert_episodes = False
    convert_seasons = False
    allow_seasons = True
    allow_episodes = True

    @cached_property
    def input_rating(self):
        from xbmcgui import Dialog
        try:
            x = int(Dialog().numeric(0, f'{self.name} (0-100)'))
        except ValueError:
            return
        if x < 0 or x > 100:
            return
        return round((x / 10) * 2) / 2

    @cached_property
    def post_response_args(self):
        args = [self.tmdb_type, self.tmdb_id]
        if self.episode is not None and self.season is not None:
            args += ['season', self.season, 'episode', self.episode]
        args.append(self.tmdb_list_type)
        return args

    def get_post_response_data(self):
        if not self.input_rating:
            return
        return {"value": f'{self.input_rating}'}

    @cached_property
    def post_response_method(self):
        if not self.input_rating:
            return 'json_delete'
        return 'json'

    @busy_decorator
    def get_sync_response(self):
        """ Called after user selects choice """
        if self.input_rating is None:
            return
        return self.tmdb_user_api.get_authorised_response_json_v3(
            *self.post_response_args,
            postdata=self.post_response_data,
            method=self.post_response_method,
        )

    def get_sync_value(self):
        return
