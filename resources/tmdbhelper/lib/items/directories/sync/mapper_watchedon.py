from datetime import timezone
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import convert_timestamp, format_date_obj
from tmdbhelper.lib.items.directories.mapper_basic import ItemMapper
from tmdbhelper.lib.items.itemlist import ItemMappingBasicFactory


class WatchedOnItemMapper(ItemMapper):
    """Add the selected watched-date components to a standard sync item."""

    @cached_property
    def mapped_item(self):
        return self.get_mapped_item()

    def get_mapped_item(self):
        entry = self.meta['entry']
        return ItemMappingBasicFactory(
            entry, item_type=entry['mediatype'], params_def=self.meta['params_def']).get_item()

    @cached_property
    def watched_date(self):
        return self.get_watched_date()

    def get_watched_date(self):
        watched_date = convert_timestamp(self.meta['entry']['last_watched_at'])
        return watched_date.replace(tzinfo=timezone.utc).astimezone()

    @cached_property
    def label(self):
        return self.mapped_item['label']

    def get_infolabels(self):
        return self.mapped_item['infolabels']

    def get_unique_ids(self):
        return self.mapped_item['unique_ids']

    def get_params(self):
        return self.mapped_item['params']

    def get_infoproperties(self):
        watched_on = self.meta['watched_on']
        infoproperties = self.mapped_item.get('infoproperties', {}).copy()
        infoproperties.update({
            key: format_date_obj(self.watched_date, date_format)
            for key, value, date_format in (
                ('month', watched_on.month, '%B'),
                ('day', watched_on.day or watched_on.weekday, '%A'),
                ('year', watched_on.year, '%Y'),
            ) if value is not None
        })
        return infoproperties

    def get_item(self):
        item = super().get_item()
        item['path'] = self.mapped_item['path']
        return item
