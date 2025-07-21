from tmdbhelper.lib.script.sync.tmdb.item import ItemSync
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.addon.plugin import get_localized


class ItemRating(ItemSync):
    localized_name_add = 32485
    localized_name_rem = 32530
    tmdb_list_type = 'rating'
    convert_episodes = False
    convert_seasons = False
    allow_seasons = True
    allow_episodes = True

    @cached_property
    def input_rating_options(self):
        input_rating_options = [0] + [x for x in reversed(range(5, 105, 5))]
        return input_rating_options

    @cached_property
    def input_rating_choices(self):
        return [
            get_localized(38022) if x == 0 else f'{get_localized(563)}: {x}%'
            for x in self.input_rating_options
        ]

    @cached_property
    def input_rating(self):
        from xbmcgui import Dialog
        x = Dialog().select(self.item_name, self.input_rating_choices, preselect=self.preselect)
        if x == -1:
            return
        # TMDb API requires rating to be out of 10 and only accepts .5 increments
        return round((self.input_rating_options[x] / 10) * 2) / 2

    @cached_property
    def preselect(self):
        try:
            return self.input_rating_options.index(self.sync_value)
        except (ValueError, TypeError, AttributeError):
            return 0

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
        return 'json' if self.input_rating else 'json_delete'

    @busy_decorator
    def get_sync_response(self):
        """ Called after user selects choice """
        if self.input_rating is None:
            return
        sync_response = self.tmdb_user_api.get_authorised_response_json_v3(
            *self.post_response_args,
            postdata=self.post_response_data,
            method=self.post_response_method,
        )
        # Force ratings database to update so we have the new data immediately
        self.query_database.get_user_ratings(
            self.tmdb_type,
            self.tmdb_id,
            self.season,
            self.episode,
            forced=True
        )
        self.name = self.get_updated_name()
        return sync_response

    def get_sync_value(self):
        return self.query_database.get_user_ratings(
            self.tmdb_type,
            self.tmdb_id,
            self.season,
            self.episode
        )

    def get_updated_name(self):
        if not self.input_rating:
            return get_localized(32530)  # Delete Rating
        if not self.sync_value:
            return f'{get_localized(32485)}: {int(self.input_rating * 10)}%'  # Add Rating
        return f'{get_localized(32489)}: {int(self.input_rating * 10)}%'  # Change Rating

    def get_name(self):
        if not self.sync_value:
            return get_localized(32485)
        return f'{get_localized(32489)}: {self.sync_value}%'
