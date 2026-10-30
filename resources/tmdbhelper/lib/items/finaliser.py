from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.filters import is_excluded


class ListFinaliser:
    def __init__(self, container, items):
        self.container = container
        self.list_items = items

    @cached_property
    def finalisers(self):
        return self.get_finalisers()

    def get_finalisers(self):
        return [
            self.container.get_item_finaliser(item)
            for item in self.list_items if item
        ]

    def prepare_kodi_details(self):
        try:
            prepare_listitems = self.container.kodi_db.prepare_listitems
        except AttributeError:  # Some directories use a library index without detail enrichment.
            return
        prepare_listitems([
            item.list_item for item in self.finalisers
            if item and item.is_visible
        ])

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        self.prepare_kodi_details()
        return [item.item if item else None for item in self.finalisers]


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
    def has_unaired_formatting(self):
        self.list_item.format_unaired_labels = self.get_unaired_formatting()
        return self.list_item.format_unaired_labels

    def get_unaired_formatting(self):
        if not self.container.format_unaired_labels:
            return False
        if self.list_item.infoproperties.get('specialseason'):
            return False
        return True

    @cached_property
    def is_visible(self):
        if not self.has_unaired_formatting:
            return True
        if self.container.hide_unaired and self.list_item.is_unaired:
            return False
        if self.container.only_unaired and not self.list_item.is_unaired:
            return False
        return True

    @cached_property
    def is_excluded(self):
        self.has_kodi_details   # Must add kodi_details first for filtering
        return is_excluded(self.list_item, is_listitem=True, **self.container.filters)

    @cached_property
    def has_kodi_details(self):
        return self.set_kodi_details(self.get_kodi_details())

    def get_kodi_details(self):
        try:
            return self.container.kodi_db.get_kodi_details(self.list_item)
        except AttributeError:
            return

    def set_kodi_details(self, kodi_details):
        if not kodi_details:
            return
        self.list_item.set_details(details=kodi_details, reverse=self.container.kodi_db_preferred)
        return kodi_details

    def get_item(self):
        if not self.is_visible:
            return

        self.has_unaired_formatting
        self.has_kodi_details

        if self.is_excluded:
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
