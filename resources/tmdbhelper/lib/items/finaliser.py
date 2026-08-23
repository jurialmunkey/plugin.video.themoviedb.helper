from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.filters import is_excluded


class ItemFinaliserBasic:
    def __init__(self, container, list_item):
        self.container = container  # parent container class
        self.list_item = list_item

    @cached_property
    def item(self):
        return self.get_item()

    is_visible = False
    is_excluded = True

    def get_item(self):
        return


class ItemFinaliserMedia(ItemFinaliserBasic):
    @cached_property
    def format_unaired_labels(self):
        if not self.container.format_unaired_labels:
            return False
        if self.list_item.infoproperties.get('specialseason'):
            return False
        return True

    @cached_property
    def is_visible(self):
        if not self.format_unaired_labels:
            return True
        if self.container.hide_unaired and self.list_item.is_unaired:
            return False
        if self.container.only_unaired and not self.list_item.is_unaired:
            return False
        return True

    @cached_property
    def is_excluded(self):
        return is_excluded(self.list_item, is_listitem=True, **self.container.filters)

    @cached_property
    def kodi_details(self):
        try:
            return self.container.kodi_db.get_kodi_details(self.list_item)
        except AttributeError:
            return

    def get_item(self):
        if not self.is_visible:
            return

        self.list_item.format_unaired_labels = self.format_unaired_labels
        self.list_item.set_details(details=self.kodi_details, reverse=self.container.kodi_db_preferred)

        if self.is_excluded:  # Filter out items that are excluded (done after adding Kodi details so can filter against them)
            return

        self.list_item.context_additions = self.container.context_additions
        self.list_item.thumb_override = self.container.thumb_override
        self.list_item.infoproperties_additions['widget'] = self.container.plugin_category
        self.list_item.infoproperties_additions.update(self.container.property_params)

        return self.list_item.finalise()


class ItemFinaliserPages(ItemFinaliserBasic):
    def get_item(self):
        self.list_item.params['cacheonly'] = self.container.is_cacheonly
        self.list_item.params['plugin_category'] = self.container.plugin_category  # Carry the plugin category to next page in plugin:// path
        return self.list_item.finalise()


def ItemFinaliser(container, list_item):
    try:
        if list_item.next_page:
            return ItemFinaliserPages(container, list_item)
        return ItemFinaliserMedia(container, list_item)
    except AttributeError:
        return
