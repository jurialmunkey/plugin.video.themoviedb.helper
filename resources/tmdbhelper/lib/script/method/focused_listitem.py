# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import parse_paramstring
from tmdbhelper.lib.addon.plugin import get_infolabel
from tmdbhelper.lib.files.futils import read_file


class FocusedListItemMedia:

    dbtype = None
    tmdb_type = None

    @cached_property
    def filename_and_path(self):
        return get_infolabel('ListItem.FileNameAndPath') or ''

    @cached_property
    def is_strm(self):
        return bool(self.filename_and_path[-5:] == '.strm')

    @cached_property
    def url(self):
        url = self.filename_and_path
        url = read_file(url) if self.is_strm else url
        return url

    @cached_property
    def url_paramstring(self):
        if not self.is_tmdbhelper:
            return ''
        try:
            return self.url.split('?')[1]
        except IndexError:
            return ''

    @cached_property
    def is_tmdbhelper(self):
        return self.url.startswith('plugin://plugin.video.themoviedb.helper/?')

    @cached_property
    def params(self):
        params = parse_paramstring(self.url_paramstring)
        return params if params.get('info') in ('play', 'details') else {}


class FocusedListItemMovie(FocusedListItemMedia):
    dbtype = 'movie'
    tmdb_type = 'movie'

    @cached_property
    def tmdb_id(self):
        return get_infolabel('ListItem.UniqueId(tmdb)')

    @cached_property
    def imdb_id(self):
        return get_infolabel('ListItem.UniqueId(imdb)')

    @cached_property
    def query(self):
        return get_infolabel('ListItem.Title')

    @cached_property
    def year(self):
        return get_infolabel('ListItem.Year')


class FocusedListItemEpisode(FocusedListItemMedia):
    dbtype = 'episode'
    tmdb_type = 'tv'

    @cached_property
    def query(self):
        return get_infolabel('ListItem.TVShowTitle')

    @cached_property
    def ep_year(self):
        return get_infolabel('ListItem.Year')

    @cached_property
    def season(self):
        return get_infolabel('ListItem.Season')

    @cached_property
    def episode(self):
        return get_infolabel('ListItem.Episode')


def FocusedListItem():
    dbtype = get_infolabel('ListItem.DBType')
    routes = {
        'movie': FocusedListItemMovie,
        'episode': FocusedListItemEpisode,
    }
    try:
        return routes[dbtype]()
    except KeyError:
        return
