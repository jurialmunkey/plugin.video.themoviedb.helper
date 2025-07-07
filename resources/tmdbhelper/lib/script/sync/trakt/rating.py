from tmdbhelper.lib.script.sync.trakt.item import ItemSync
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.addon.dialog import busy_decorator
from xbmcgui import Dialog


class ItemRating(ItemSync):
    allow_episodes = True
    localized_name_add = 32485
    localized_name_rem = 32489
    trakt_sync_key = 'rating'

    def get_name_remove(self):
        return f'{get_localized(self.localized_name_rem)} ({self.sync_value})'

    @staticmethod
    def refresh_containers():
        pass  # Override

    def get_dialog_header(self):
        rating = self.sync_item.get('rating')
        if rating == 0:
            return get_localized(32530)  # Remove rating
        if self.name == get_localized(32485):
            return f'{get_localized(32485)} ({rating})'  # Add Rating (rating)
        return f'{get_localized(32489)} ({rating})'  # Change Rating (rating)

    @busy_decorator
    def set_rating(self, x):
        return self.trakt_api.post_response('sync', 'ratings/remove' if x == 0 else 'ratings', postdata={f'{self.trakt_type}s': [self.sync_item]})

    def get_sync_response(self):
        # Ask user for rating
        try:
            x = int(Dialog().numeric(0, f'{self.name} (0-10)'))
        except ValueError:
            return

        if x < 0 or x > 10:
            return

        self.sync_item['rating'] = x
        return self.set_rating(x)
