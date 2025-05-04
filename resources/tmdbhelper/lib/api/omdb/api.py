from jurialmunkey.parser import del_empty_keys, merge_two_dicts
from tmdbhelper.lib.api.request import RequestAPI
from tmdbhelper.lib.api.omdb.mapping import ItemMapper
from tmdbhelper.lib.api.api_keys.omdb import API_KEY


def translate_xml(request):
    """ Workaround wrapper for broken ElementTree in Python 3.11.1 """

    if not request:
        return

    from xml.dom.minidom import parseString
    from xml.parsers.expat import ExpatError

    try:
        r = parseString(request.text)
        d = {k: v for k, v in r.firstChild.firstChild.attributes.items() if k and v}
    except AttributeError:
        return
    except ExpatError:
        return

    return {'root': {'movie': [d]}}


class OMDb(RequestAPI):

    api_key = API_KEY

    def __init__(self, api_key=None):
        api_key = api_key or self.api_key

        super(OMDb, self).__init__(
            req_api_key=f'apikey={api_key}',
            req_api_name='OMDb',
            req_api_url='https://www.omdbapi.com/')
        self.translate_xml = translate_xml  # Temp monkey patch bandaid for broken ElementTree. Remove after upstream fix.
        self._error_notification = False  # Override user settings and always suppress OMDb error notifications since it times-out a lot.
        OMDb.api_key = api_key

    def get_request_item(self, imdb_id=None, title=None, year=None, tomatoes=True, fullplot=True, cache_only=False):
        kwparams = {}
        kwparams['i'] = imdb_id
        kwparams['t'] = title
        kwparams['y'] = year
        kwparams['plot'] = 'full' if fullplot else 'short'
        kwparams['tomatoes'] = 'True' if tomatoes else None
        kwparams = del_empty_keys(kwparams)
        request = self.get_request_lc(is_xml=True, cache_only=cache_only, r='xml', **kwparams)
        try:
            request = request['root']['movie'][0]
        except (KeyError, TypeError, AttributeError):
            request = {}
        return request

    def get_ratings_awards(self, imdb_id=None, title=None, year=None, cache_only=False):
        request = self.get_request_item(imdb_id=imdb_id, title=title, year=year, cache_only=cache_only)
        return ItemMapper().get_info(request)
