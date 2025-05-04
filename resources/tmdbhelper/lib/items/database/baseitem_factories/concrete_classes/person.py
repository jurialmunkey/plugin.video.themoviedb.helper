from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.baseclass import BaseItem


class Person(BaseItem):
    table = 'person'
    tmdb_type = 'person'
    ftv_id = None

    @staticmethod
    def unaired_expiry(*args, **kwargs):
        return  # People dont have premiered dates so we dont modify expiry time

    @property
    def online_data_kwgs(self):
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response_person}

    @property
    def db_table_caches(self):
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('movie'),
            self.return_basemeta_db('tvshow'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('castmember'),
            self.return_basemeta_db('crewmember'),
            self.return_basemeta_db('art'),
        )
