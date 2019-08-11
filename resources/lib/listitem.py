from globals import _addonpath, IMAGEPATH, _handle
from utils import get_url
import utils
import xbmcgui
import xbmcplugin


class ListItem:
    def __init__(self):
        self.name = ''  # ListItem.Label,Title
        self.label2 = ''  # ListItem.Label2
        self.dbtype = ''  # ListItem.DBType
        self.library = ''  # <content target= video, music, pictures, none>
        self.tmdb_id = ''  # ListItem.Property(tmdb_id)
        self.imdb_id = ''  # IMDb ID for item
        self.dbid = ''  # ListItem.DBID
        self.request_tmdb_type = ''  # The TMDb DBType for the Request
        self.request_tmdb_id = ''  # The TMDb ID for the Request
        self.plural_type = ''  # Plural form of category type
        self.kwparams = {}  # kwparams to contruct ListItem.FolderPath (plugin path call)
        self.poster = _addonpath + '/resources/poster.png'  # Icon, Thumb, Poster
        self.fanart = _addonpath + '/fanart.jpg'  # Fanart
        self.cast = []  # Cast list
        self.is_folder = True
        self.detailed_info = {}  # Additional info gathered if cached detailed tmdb item
        self.omdb_info = {}  # Additional info gathered if cached detailed omdb item
        self.infolabels = {}  # The item info
        self.infoproperties = {}  # The item properties
        self.infoart = {'thumb': self.poster,
                        'icon': self.poster,
                        'poster': self.poster,
                        'fanart': self.fanart}

    def get_tmdb_id(self, request_item):
        if request_item.get('id'):
            self.tmdb_id = request_item.get('id')

    def get_title(self, request_item):
        if request_item.get('title'):
            self.name = request_item.get('title')
        elif request_item.get('name'):
            self.name = request_item.get('name')
        elif request_item.get('author'):
            self.name = request_item.get('author')
        elif request_item.get('width') and request_item.get('height'):
            self.name = '{0}x{1}'.format(request_item.get('width'), request_item.get('height'))
        else:
            self.name = 'N/A'

    def get_fanart(self, request_item):
        if request_item.get('backdrop_path'):
            self.fanart = IMAGEPATH + request_item.get('backdrop_path')
        self.infoart['fanart'] = self.fanart

    def get_poster(self, request_item):
        if request_item.get('poster_path'):
            self.poster = IMAGEPATH + request_item.get('poster_path')
        elif request_item.get('profile_path'):
            self.poster = IMAGEPATH + request_item.get('profile_path')
        elif request_item.get('file_path'):
            self.poster = IMAGEPATH + request_item.get('file_path')
        self.infoart['poster'] = self.poster
        self.infoart['thumb'] = self.poster
        self.infoart['icon'] = self.poster

    def get_info(self, request_item):
        self.infolabels['title'] = self.name
        self.imdb_id = request_item.get('imdb_id')
        if self.dbid:
            self.infolabels['dbid'] = self.dbid
        if request_item.get('overview'):
            self.infolabels['plot'] = request_item.get('overview')
        elif request_item.get('biography'):
            self.infolabels['plot'] = request_item.get('biography')
        elif request_item.get('content'):
            self.infolabels['plot'] = request_item.get('content')
        if request_item.get('vote_average'):
            self.infolabels['rating'] = request_item.get('vote_average')
            self.label2 = request_item.get('vote_average')
        if request_item.get('vote_count'):
            self.infolabels['votes'] = request_item.get('vote_count')
        if request_item.get('release_date'):
            self.infolabels['premiered'] = request_item.get('release_date')
            self.infolabels['year'] = request_item.get('release_date')[:4]
        if request_item.get('imdb_id'):
            self.infolabels['imdbnumber'] = request_item.get('imdb_id')
        if request_item.get('runtime'):
            self.infolabels['duration'] = request_item.get('runtime') * 60
        if request_item.get('tagline'):
            self.infolabels['tagline'] = request_item.get('tagline')
        if request_item.get('status'):
            self.infolabels['status'] = request_item.get('status')
        if request_item.get('genres'):
            self.infolabels['genre'] = utils.dict_to_list(request_item.get('genres'), 'name')
        if request_item.get('production_companies'):
            self.infolabels['studio'] = utils.dict_to_list(request_item.get('production_companies'), 'name')
        if request_item.get('production_countries'):
            self.infolabels['country'] = utils.dict_to_list(request_item.get('production_countries'), 'name')
        if request_item.get('belongs_to_collection'):
            self.infolabels['set'] = request_item.get('belongs_to_collection').get('name')

    def get_properties(self, request_item):
        self.infoproperties['tmdb_id'] = self.tmdb_id
        self.infoproperties['imdb_id'] = self.imdb_id
        if request_item.get('genres'):
            self.infoproperties = utils.iter_props(request_item.get('genres'), 'Genre', self.infoproperties, name='name', tmdb_id='id')
        if request_item.get('production_companies'):
            self.infoproperties = utils.iter_props(request_item.get('production_companies'), 'Studio', self.infoproperties, name='name', tmdb_id='id')
        if request_item.get('production_countries'):
            self.infoproperties = utils.iter_props(request_item.get('production_countries'), 'Country', self.infoproperties, name='name', tmdb_id='id')
        if request_item.get('biography'):
            self.infoproperties['biography'] = request_item.get('biography')
        if request_item.get('birthday'):
            self.infoproperties['birthday'] = request_item.get('birthday')
            self.infoproperties['age'] = utils.age_difference(request_item.get('birthday'), request_item.get('deathday'))
        if request_item.get('deathday'):
            self.infoproperties['deathday'] = request_item.get('deathday')
        if request_item.get('also_know_as'):
            self.infoproperties['aliases'] = request_item.get('also_know_as')
        if request_item.get('known_for_department'):
            self.infoproperties['role'] = request_item.get('known_for_department')
        if request_item.get('place_of_birth'):
            self.infoproperties['born'] = request_item.get('place_of_birth')
        if request_item.get('character'):
            self.infoproperties['character'] = request_item.get('character')
            self.label2 = request_item.get('character')
        if request_item.get('department'):
            self.infoproperties['department'] = request_item.get('department')
            self.label2 = request_item.get('department')
        if request_item.get('job'):
            self.infoproperties['job'] = request_item.get('job')
            self.label2 = request_item.get('job')
        if request_item.get('known_for'):
            self.infoproperties['known_for'] = utils.concatinate_names(request_item.get('known_for'), 'title', '/')
            self.infoproperties = utils.iter_props(request_item.get('known_for'), 'known_for', self.infoproperties, title='title', tmdb_id='id', rating='vote_average', tmdb_type='media_type')
        if request_item.get('budget'):
            self.infoproperties['budget'] = '${:0,.0f}'.format(request_item.get('budget'))
        if request_item.get('revenue'):
            self.infoproperties['revenue'] = '${:0,.0f}'.format(request_item.get('revenue'))
        if request_item.get('belongs_to_collection'):
            self.infoproperties['set.tmdb_id'] = request_item.get('belongs_to_collection').get('id')
            self.infoproperties['set.name'] = request_item.get('belongs_to_collection').get('name')
            self.infoproperties['set.poster'] = IMAGEPATH + request_item.get('belongs_to_collection').get('poster_path')
            self.infoproperties['set.fanart'] = IMAGEPATH + request_item.get('belongs_to_collection').get('backdrop_path')

    def get_omdb_info(self, request_item):
        if request_item.get('rated'):
            self.infolabels['MPAA'] = 'Rated ' + request_item.get('rated')
        if request_item.get('awards'):
            self.infoproperties['awards'] = request_item.get('awards')
        if request_item.get('metascore'):
            self.infoproperties['metacritic_rating'] = request_item.get('metascore')
        if request_item.get('imdbRating'):
            self.infoproperties['imdb_rating'] = request_item.get('imdbRating')
        if request_item.get('imdbVotes'):
            self.infoproperties['imdb_votes'] = request_item.get('imdbVotes')
        if request_item.get('tomatoMeter'):
            self.infoproperties['rottentomatoes_rating'] = request_item.get('tomatoMeter')
        if request_item.get('tomatoImage'):
            self.infoproperties['rottentomatoes_image'] = request_item.get('tomatoImage')
        if request_item.get('tomatoReviews'):
            self.infoproperties['rottentomatoes_reviewtotal'] = request_item.get('tomatoReviews')
        if request_item.get('tomatoFresh'):
            self.infoproperties['rottentomatoes_reviewsfresh'] = request_item.get('tomatoFresh')
        if request_item.get('tomatoRotten'):
            self.infoproperties['rottentomatoes_reviewsrotten'] = request_item.get('tomatoRotten')
        if request_item.get('tomatoConsensus'):
            self.infoproperties['rottentomatoes_consensus'] = request_item.get('tomatoConsensus')
        if request_item.get('tomatoUserMeter'):
            self.infoproperties['rottentomatoes_usermeter'] = request_item.get('tomatoUserMeter')
        if request_item.get('tomatoUserReviews'):
            self.infoproperties['rottentomatoes_userreviews'] = request_item.get('tomatoUserReviews')

    def get_cast(self, request_item):
        if request_item.get('credits'):
            if request_item.get('credits').get('cast'):
                x = 1
                for item in request_item.get('credits').get('cast'):
                    if item.get('name'):
                        cast_member = {}
                        cast_member['name'] = item.get('name')
                        cast_member['role'] = item.get('character')
                        cast_member['order'] = item.get('order')
                        cast_member['thumbnail'] = IMAGEPATH + item.get('profile_path') if item.get('profile_path') else ''
                        p = 'Cast.' + str(x) + '.'
                        self.infoproperties[p + 'name'] = cast_member.get('name')
                        self.infoproperties[p + 'role'] = cast_member.get('role')
                        self.infoproperties[p + 'thumb'] = cast_member.get('thumbnail')
                        self.cast.append(cast_member)
                        x = x + 1
            if request_item.get('credits').get('crew'):
                x = 1
                for item in request_item.get('credits').get('crew'):
                    if item.get('name'):
                        p = 'Crew.' + str(x) + '.'
                        self.infoproperties[p + 'name'] = item.get('name')
                        self.infoproperties[p + 'job'] = item.get('job')
                        self.infoproperties[p + 'department'] = item.get('department')
                        self.infoproperties[p + 'thumb'] = IMAGEPATH + item.get('profile_path') if item.get('profile_path') else ''
                        if item.get('job') == 'Director':
                            self.infolabels.setdefault('director', []).append(item.get('name'))
                        if item.get('department') == 'Writing':
                            self.infolabels.setdefault('writer', []).append(item.get('name'))
                        x = x + 1

    def get_autofilled_info(self, item):
        self.get_poster(item)
        self.get_fanart(item)
        self.get_tmdb_id(item)
        self.get_info(item)
        self.get_properties(item)
        self.get_cast(item)

    def get_dbtypes(self, tmdb_type):
        self.plural_type = utils.convert_to_plural_type(tmdb_type)
        self.library = utils.convert_to_library_type(tmdb_type)
        self.dbtype = utils.convert_to_kodi_type(tmdb_type)
        self.infolabels['mediatype'] = self.dbtype
        self.infoproperties['tmdb_type'] = tmdb_type

    def create_kwparams(self, next_type, next_info, **kwargs):
        self.kwparams['type'] = next_type
        self.kwparams['info'] = next_info
        self.kwparams['tmdb_id'] = self.tmdb_id
        for key, value in kwargs.items():
            if value:
                self.kwparams[key] = value

    def create_listitem(self, **kwargs):
        self.listitem = xbmcgui.ListItem(label=self.name, label2=self.label2)
        self.listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': self.tmdb_id})

        self.listitem.setInfo(self.library, self.infolabels)
        self.listitem.setProperties(self.infoproperties)
        self.listitem.setArt(self.infoart)
        self.listitem.setCast(self.cast)
        if kwargs.get('info') == 'textviewer':
            self.url = get_url(info='textviewer')
        elif kwargs.get('info') == 'imageviewer':
            self.url = get_url(info='imageviewer', image=self.poster)
        else:
            self.url = get_url(**kwargs)
        xbmcplugin.addDirectoryItem(_handle, self.url, self.listitem, self.is_folder)
