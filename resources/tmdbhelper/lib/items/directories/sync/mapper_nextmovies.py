from datetime import timezone
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_infolabel, get_localized
from tmdbhelper.lib.addon.tmdate import convert_timestamp, format_date_obj
from tmdbhelper.lib.items.directories.mapper_basic import ItemMapper
from tmdbhelper.lib.items.itemlist import ItemMappingBasicFactory


class NextMovieItemMapper(ItemMapper):
    @cached_property
    def mapped_item(self):
        return self.get_mapped_item()

    def get_mapped_item(self):
        return ItemMappingBasicFactory({'id': self.meta['tmdb_id']}, item_type='movie').get_item()

    @cached_property
    def label(self):
        return self.mapped_item['label']

    def get_infolabels(self):
        return dict(self.mapped_item['infolabels'], premiered=self.meta['premiered'])

    def get_params(self):
        return self.mapped_item['params']

    def get_unique_ids(self):
        return self.mapped_item['unique_ids']

    def get_context_menu(self):
        command = (
            'RunScript(plugin.video.themoviedb.helper,drop_collection,'
            f'collection_id={self.meta["collection_id"]})')
        return super().get_context_menu() + [(get_localized(32607), command)]

    def get_infoproperties(self):
        properties = {
            key: self.meta[key]
            for key in ('collection_id', 'collection_position', 'collection_total', 'collection_reset_at')
        }
        properties.update(self.reset_properties)
        return properties

    @cached_property
    def reset_datetime(self):
        return self.get_reset_datetime()

    def get_reset_datetime(self):
        return convert_timestamp(self.meta['collection_reset_at']).replace(tzinfo=timezone.utc).astimezone()

    @cached_property
    def reset_properties(self):
        return self.get_reset_properties()

    def get_reset_properties(self):
        if not self.meta['collection_reset_at']:
            return {}
        date_format = get_infolabel('Skin.String(TMDbHelper.Date.Format)') or '%d %b %Y'
        return {
            'collection_reset_date': format_date_obj(self.reset_datetime, date_format),
            'collection_reset_date_long': format_date_obj(self.reset_datetime, region_fmt='datelong'),
        }

    def get_item(self):
        item = super().get_item()
        item['path'] = self.mapped_item['path']
        return item
