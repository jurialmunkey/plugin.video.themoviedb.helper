from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.mappings import ItemMapperMethods


class BaseItem:
    art_dbclist_routes = ()
    infolabels_dbclist_routes = ()
    infolabels_dbcitem_routes = ()
    infoproperties_dbcitem_routes = ()
    infoproperties_dbclist_routes = ()
    extendedinfo = False
    parent_db_cache = None
    data = None

    def __init__(self, parent_db_cache):
        self.parent_db_cache = parent_db_cache

    def return_basemeta_db(self, *args, **kwargs):
        return self.parent_db_cache.return_basemeta_db(*args, **kwargs)

    @staticmethod
    def get_subtype_key(key, subtype=None):
        return f"{subtype}.{key}" if subtype else key

    @staticmethod
    def get_configured_item_value(i, ikey, instance):
        if ikey == 'backdrop':
            return instance.image_path_backdrop_func(i[ikey])
        if ikey in ('thumb', 'logo'):
            return instance.image_path_func(i[ikey])
        return i[ikey]

    def get_data_value(self, key):
        try:
            return self.data[0][key]
        except(KeyError, TypeError, IndexError, AttributeError):
            return

    def get_instance_cached_data_value(self, instance, key):
        try:
            return instance.cached_data[0][key]
        except(KeyError, TypeError, IndexError, AttributeError):
            return

    def get_infolabels_dbclist(self, infolabels):
        for instance, ikey, dkey in self.infolabels_dbclist_routes:
            instance = self.return_basemeta_db(*instance)
            try:
                data = [i[ikey] for i in instance.cached_data]
                if not data:
                    continue
                infolabels[dkey] = data
            except(KeyError, TypeError, IndexError, AttributeError):
                pass
        return infolabels

    def get_infolabels_dbcitem(self, infolabels):
        for instance, ikey, dkey in self.infolabels_dbcitem_routes:
            instance = self.return_basemeta_db(*instance)
            try:
                data = ikey(instance.cached_data[0]) if callable(ikey) else instance.cached_data[0][ikey]
                if data is None:
                    continue
                infolabels[dkey] = data
            except(KeyError, TypeError, IndexError, AttributeError):
                pass
        return infolabels

    def get_infolabels_special(self, infolabels):
        return infolabels

    def get_infoproperties_airdate(self, infoproperties):
        infoproperties.update(ItemMapperMethods.get_custom_time(self.get_data_value('duration'), name='duration'))
        infoproperties.update(ItemMapperMethods.get_custom_date(self.get_data_value('premiered'), name='premiered'))
        return infoproperties

    def get_infolabels_details(self):
        infolabels = {'mediatype': self.mediatype}
        infolabels.update({k: self.data[0][k] for k in self.data[0].keys() if k in self.parent_db_cache.allowlist_infolabel_keys})
        return infolabels

    def get_infoproperties_dbclist(self, infoproperties):
        for d in self.infoproperties_dbclist_routes:
            instance = d['instance']
            mappings = d['mappings']
            propname = d['propname']
            joinings = d['joinings']
            instance = self.return_basemeta_db(*instance)
            for x, i in enumerate(instance.cached_data, 1):
                for dkey, ikey in mappings.items():
                    data = self.get_configured_item_value(i, ikey, instance)
                    if data is None:
                        continue
                    for name in propname:
                        infoproperties[f'{name}.{x}.{dkey}'] = data
            if joinings is None:
                continue
            join_data = [i[joinings[1]] for i in instance.cached_data if i[joinings[1]]]
            infoproperties[joinings[0]] = ' / '.join(join_data)
            infoproperties[f'{joinings[0]}_CR'] = '[CR]'.join(join_data)
        return infoproperties

    def get_infoproperties_dbcitem(self, infoproperties):
        for instance, ikey, dkey in self.infoproperties_dbcitem_routes:
            instance = self.return_basemeta_db(*instance)
            try:
                data = ikey(instance.cached_data[0]) if callable(ikey) else instance.cached_data[0][ikey]
                if data is None:
                    continue
                infoproperties[dkey] = data
            except(KeyError, TypeError, IndexError, AttributeError):
                pass
        return infoproperties

    def get_infoproperties_special(self, infoproperties):
        return infoproperties

    def get_art_dbclist(self, art):
        for instance, dkey in self.art_dbclist_routes:
            attr, subtype = instance
            instance = self.return_basemeta_db(attr, subtype)

            try:
                datalist = instance.cached_data if attr == 'art_extrafanart' else [instance.cached_data[0]]
            except(KeyError, TypeError, IndexError, AttributeError):
                continue
            x = 0
            for i in datalist:

                url = i['icon']
                if not url:
                    continue

                if attr == 'art_extrafanart':
                    x += 1
                    this_dkey = f'{dkey}{x}'
                else:
                    this_dkey = dkey

                url = instance.image_path_func(url)

                art[this_dkey] = art.get(this_dkey) or url

                if not subtype:
                    continue

                subtype_dkey = f'{subtype}.{this_dkey}'
                art[subtype_dkey] = art.get(subtype_dkey) or url

        return art

    def get_unique_ids(self, unique_ids):
        return unique_ids

    @cached_property
    def infolabels(self):
        infolabels = self.get_infolabels_details()
        infolabels = self.get_infolabels_dbclist(infolabels)
        infolabels = self.get_infolabels_dbcitem(infolabels)
        infolabels = self.get_infolabels_special(infolabels)
        return infolabels

    @cached_property
    def infoproperties(self):
        infoproperties = self.get_infoproperties_dbclist({}) if self.extendedinfo else {}
        infoproperties = self.get_infoproperties_dbcitem(infoproperties)
        infoproperties = self.get_infoproperties_special(infoproperties)
        infoproperties = self.get_infoproperties_airdate(infoproperties)
        return infoproperties

    @cached_property
    def cast(self):
        return []

    @cached_property
    def art(self):
        art = {}
        art = self.get_art_dbclist(art)
        return art

    @cached_property
    def unique_ids(self):
        unique_ids = {}
        unique_ids = self.get_unique_ids(unique_ids)
        return unique_ids

    @cached_property
    def item(self):
        return {
            'mediatype': self.mediatype,
            'infolabels': self.infolabels,
            'infoproperties': self.infoproperties,
            'cast': self.cast,
            'art': self.art,
            'unique_ids': self.unique_ids,
        }
