from jurialmunkey.ftools import cached_property


class FindQueriesDatabaseProviderRegions:

    provider_regions_columns = {
        'iso_3166_1': {
            'data': 'TEXT PRIMARY KEY',
            'indexed': True
        },
        'native_name': {
            'data': 'TEXT'
        },
    }

    """
    provider_regions
    """
    @cached_property
    def provider_regions(self):
        return self.get_provider_regions()

    def get_provider_regions(self):
        table = 'provider_regions'
        keys = ('iso_3166_1', 'native_name', )

        def get_data():
            provider_regions = self.tmdb_api.get_response_json('watch', 'providers', 'regions') or {}
            provider_regions = provider_regions.get('results')
            return {i['iso_3166_1']: i['native_name'] for i in provider_regions if i} if provider_regions else {}

        def configure_dict(provider_regions):
            return {i['iso_3166_1']: i['native_name'] for i in provider_regions} if provider_regions else {}

        def get_cached():
            return self.get_cached_values(table, keys, configure_dict)

        def set_cached():
            data = get_data()
            if not data:
                return
            values = [(iso_3166_1, native_name) for iso_3166_1, native_name in data.items()]
            self.set_cached_values(table, keys, values)
            return get_cached()

        return get_cached() or set_cached()
