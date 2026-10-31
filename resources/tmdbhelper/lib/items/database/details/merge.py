from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import merge_two_dicts


class ItemDetailsMerger:
    """Merge details into a list item's data.

    Values already on the list item win unless reverse is set. Shared by list items in
    the plugin and by the item detail service so that both merge in the same way.
    """

    merged_dicts = ('stream_details', 'infolabels', 'infoproperties', 'art', 'unique_ids')
    item_keys = (*merged_dicts, 'cast', 'label')  # List item data needed to merge

    def __init__(self, item, details, reverse=False, override=False, reverse_artwork=False):
        self.item = item
        self.details = details
        self.reverse = reverse
        self.override = override
        self.reverse_artwork = reverse_artwork

    @cached_property
    def merged(self):
        return self.get_merged()

    def get_merged(self):
        merged = {key: self.get_merged_dict(key) for key in self.merged_dicts}
        merged['cast'] = self.item.get('cast') or self.details.get('cast', [])
        if self.override:
            self.set_overrides(merged)
        return merged

    def get_merged_dict(self, key):
        return merge_two_dicts(
            self.details.get(key, {}), self.item.get(key),
            reverse=self.is_reversed(key))

    def is_reversed(self, key):
        if key == 'art':
            return bool(self.reverse or self.reverse_artwork)
        return self.reverse

    def set_overrides(self, merged):
        infolabels = self.details.get('infolabels', {})
        merged['label'] = self.details.get('label') or self.item.get('label')
        merged['infolabels']['title'] = infolabels.get('title') or merged['infolabels'].get('title')
        merged['infolabels']['tvshowtitle'] = infolabels.get('tvshowtitle') or merged['infolabels'].get('tvshowtitle')


class ConfiguredItemMerger(ItemDetailsMerger):
    """Fill a list item with its item details: list values win except for art and titles."""

    def __init__(self, item, details):
        super().__init__(item, details, override=True, reverse_artwork=True)
