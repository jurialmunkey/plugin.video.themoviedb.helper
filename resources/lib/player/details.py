import datetime
from resources.lib.addon.constants import PLAYERS_URLENCODE
from resources.lib.tmdb.api import TMDb
from resources.lib.trakt.api import TraktAPI
from resources.lib.container.listitem import ListItem
from resources.lib.addon.plugin import viewitems
from resources.lib.addon.parser import try_int, try_encode
from resources.lib.addon.setutils import del_empty_keys
from json import dumps
from collections import defaultdict
try:
    from urllib.parse import quote_plus, quote  # Py3
except ImportError:
    from urllib import quote_plus, quote  # Py2


def get_external_ids(li, season=None, episode=None):
    trakt_api = TraktAPI()
    unique_id, trakt_type = None, None
    if li.infolabels.get('mediatype') == 'movie':
        unique_id = li.unique_ids.get('tmdb')
        trakt_type = 'movie'
    elif li.infolabels.get('mediatype') == 'tvshow':
        unique_id = li.unique_ids.get('tmdb')
        trakt_type = 'show'
    elif li.infolabels.get('mediatype') in ['season', 'episode']:
        unique_id = li.unique_ids.get('tvshow.tmdb')
        trakt_type = 'show'
    if not unique_id or not trakt_type:
        return
    trakt_slug = trakt_api.get_id(id_type='tmdb', unique_id=unique_id, trakt_type=trakt_type, output_type='slug')
    if not trakt_slug:
        return
    details = trakt_api.get_details(trakt_type, trakt_slug, extended=None)
    if not details:
        return
    if li.infolabels.get('mediatype') in ['movie', 'tvshow', 'season']:
        return {
            'unique_ids': {
                'tmdb': unique_id,
                'tvdb': details.get('ids', {}).get('tvdb'),
                'imdb': details.get('ids', {}).get('imdb'),
                'slug': details.get('ids', {}).get('slug'),
                'trakt': details.get('ids', {}).get('trakt')}}
    episode_details = trakt_api.get_details(
        trakt_type, trakt_slug,
        season=season or li.infolabels.get('season'),
        episode=episode or li.infolabels.get('episode'),
        extended=None)
    if episode_details:
        return {
            'unique_ids': {
                'tvshow.tmdb': unique_id,
                'tvshow.tvdb': details.get('ids', {}).get('tvdb'),
                'tvshow.imdb': details.get('ids', {}).get('imdb'),
                'tvshow.slug': details.get('ids', {}).get('slug'),
                'tvshow.trakt': details.get('ids', {}).get('trakt'),
                'tvdb': episode_details.get('ids', {}).get('tvdb'),
                'tmdb': episode_details.get('ids', {}).get('tmdb'),
                'imdb': episode_details.get('ids', {}).get('imdb'),
                'slug': episode_details.get('ids', {}).get('slug'),
                'trakt': episode_details.get('ids', {}).get('trakt')}}


def get_item_details(tmdb_type, tmdb_id, season=None, episode=None):
    details = TMDb().get_details(tmdb_type, tmdb_id, season, episode)
    if not details:
        return None
    details = ListItem(**details)
    details.infolabels['mediatype'] == 'movie' if tmdb_type == 'movie' else 'episode'
    details.set_details(details=get_external_ids(details, season=season, episode=episode))
    return details


def get_detailed_item(tmdb_type, tmdb_id, season=None, episode=None, details=None):
    details = details or get_item_details(tmdb_type, tmdb_id, season, episode)
    if not details:
        return None
    item = defaultdict(lambda: '+')
    item['id'] = item['tmdb'] = tmdb_id
    item['imdb'] = details.unique_ids.get('imdb')
    item['tvdb'] = details.unique_ids.get('tvdb')
    item['trakt'] = details.unique_ids.get('trakt')
    item['slug'] = details.unique_ids.get('slug')
    item['season'] = season
    item['episode'] = episode
    item['originaltitle'] = details.infolabels.get('originaltitle')
    item['title'] = details.infolabels.get('tvshowtitle') or details.infolabels.get('title')
    item['showname'] = item['clearname'] = item['tvshowtitle'] = item.get('title')
    item['year'] = details.infolabels.get('year')
    item['name'] = u'{} ({})'.format(item.get('title'), item.get('year'))
    item['premiered'] = item['firstaired'] = item['released'] = details.infolabels.get('premiered')
    item['plot'] = details.infolabels.get('plot')
    item['cast'] = item['actors'] = " / ".join([i.get('name') for i in details.cast if i.get('name')])
    item['thumbnail'] = details.art.get('thumb')
    item['poster'] = details.art.get('poster')
    item['fanart'] = details.art.get('fanart')
    item['now'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

    if tmdb_type == 'tv' and season is not None and episode is not None:
        item['id'] = item['epid'] = item['eptvdb'] = item.get('tvdb')
        item['title'] = details.infolabels.get('title')  # Set Episode Title
        item['name'] = u'{0} S{1:02d}E{2:02d}'.format(item.get('showname'), try_int(season), try_int(episode))
        item['season'] = season
        item['episode'] = episode
        item['showpremiered'] = details.infoproperties.get('tvshow.premiered')
        item['showyear'] = details.infoproperties.get('tvshow.year')
        item['eptmdb'] = details.unique_ids.get('tmdb')
        item['epimdb'] = details.unique_ids.get('imdb')
        item['eptrakt'] = details.unique_ids.get('trakt')
        item['epslug'] = details.unique_ids.get('slug')
        item['tmdb'] = details.unique_ids.get('tvshow.tmdb')
        item['imdb'] = details.unique_ids.get('tvshow.imdb')
        item['tvdb'] = details.unique_ids.get('tvshow.tvdb')
        item['trakt'] = details.unique_ids.get('tvshow.trakt')
        item['slug'] = details.unique_ids.get('tvshow.slug')

    for k, v in viewitems(item.copy()):
        if k not in PLAYERS_URLENCODE:
            continue
        v = u'{0}'.format(v)
        for key, value in viewitems({k: v, '{}_meta'.format(k): dumps(v)}):
            item[key] = value.replace(',', '')
            item[key + '_+'] = value.replace(',', '').replace(' ', '+')
            item[key + '_-'] = value.replace(',', '').replace(' ', '-')
            item[key + '_escaped'] = quote(quote(try_encode(value)))
            item[key + '_escaped+'] = quote(quote_plus(try_encode(value)))
            item[key + '_url'] = quote(try_encode(value))
            item[key + '_url+'] = quote_plus(try_encode(value))
    return item


def get_playerstring(tmdb_type, tmdb_id, season=None, episode=None, details=None):
    if not details:
        return None
    playerstring = {}
    playerstring['tmdb_type'] = 'episode' if tmdb_type in ['episode', 'tv'] else 'movie'
    playerstring['tmdb_id'] = tmdb_id
    playerstring['imdb_id'] = details.unique_ids.get('imdb')
    if tmdb_type in ['episode', 'tv']:
        playerstring['imdb_id'] = details.unique_ids.get('tvshow.imdb')
        playerstring['tvdb_id'] = details.unique_ids.get('tvshow.tvdb')
        playerstring['season'] = season
        playerstring['episode'] = episode
    return dumps(del_empty_keys(playerstring))
