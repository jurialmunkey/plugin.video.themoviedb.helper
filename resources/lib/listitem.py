from globals import _addonpath, IMAGEPATH, _handle, _mpaaprefix, _country
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
        self.plural_type = ''  # Pluralised category type used to create category folders
        self.kwparams = {}  # kwparams to contruct ListItem.FolderPath (plugin path call)
        self.poster = '{0}/resources/poster.png'.format(_addonpath)  # Poster
        self.thumb = '{0}/resources/poster.png'.format(_addonpath)  # Thumb
        self.icon = '{0}/resources/poster.png'.format(_addonpath)  # Icon
        self.fanart = '{0}/fanart.jpg'.format(_addonpath)  # Fanart
        self.cast = []  # Cast list
        self.is_folder = True
        self.infolabels = {}  # The item info
        self.infoproperties = {}  # The item properties
        self.infoart = {'thumb': self.thumb,
                        'icon': self.icon,
                        'poster': self.poster,
                        'fanart': self.fanart}

    def get_tmdb_id(self, request_item):
        if request_item.get('id'):
            self.tmdb_id = request_item.get('id')

    def get_fanart(self, request_item):
        if request_item.get('backdrop_path'):
            self.fanart = '{0}{1}'.format(IMAGEPATH, request_item.get('backdrop_path'))
        self.infoart['fanart'] = self.fanart

    def get_poster(self, request_item):
        # Get the poster
        if request_item.get('poster_path'):
            self.poster = '{0}{1}'.format(IMAGEPATH, request_item.get('poster_path'))
        elif request_item.get('profile_path'):
            self.poster = '{0}{1}'.format(IMAGEPATH, request_item.get('profile_path'))
        elif request_item.get('file_path'):
            self.poster = '{0}{1}'.format(IMAGEPATH, request_item.get('file_path'))
        # Get the season poster for episodes
        if request_item.get('season_number') and request_item.get('seasons'):
            for item in request_item.get('seasons'):
                if item.get('season_number') == request_item.get('season_number'):
                    if item.get('poster_path'):
                        self.poster = '{0}{1}'.format(IMAGEPATH, item.get('poster_path'))
                    break
        # Get the thumb still for episodes
        if request_item.get('still_path'):
            self.thumb = '{0}{1}'.format(IMAGEPATH, request_item.get('still_path'))
        else:
            self.thumb = self.poster
        self.icon = self.poster
        self.infoart['poster'] = self.poster
        self.infoart['icon'] = self.icon
        self.infoart['thumb'] = self.thumb

    def get_info(self, request_item):
        self.infolabels['title'] = self.name
        self.imdb_id = request_item.get('imdb_id', '')
        if self.dbid:
            self.infolabels['dbid'] = self.dbid
        if request_item.get('original_title'):
            self.infolabels['originaltitle'] = request_item.get('original_title')
        if request_item.get('overview'):
            self.infolabels['plot'] = request_item.get('overview')
        elif request_item.get('biography'):
            self.infolabels['plot'] = request_item.get('biography')
        elif request_item.get('content'):
            self.infolabels['plot'] = request_item.get('content')
        if request_item.get('vote_average'):
            self.infolabels['rating'] = request_item.get('vote_average')
            self.label2 = str(request_item.get('vote_average'))
        if request_item.get('vote_count'):
            self.infolabels['votes'] = request_item.get('vote_count')
        if request_item.get('first_air_date'):
            self.infolabels['premiered'] = request_item.get('first_air_date')
            self.infolabels['year'] = request_item.get('first_air_date')[:4]
        if request_item.get('release_date'):
            self.infolabels['premiered'] = request_item.get('release_date')
            self.infolabels['year'] = request_item.get('release_date')[:4]
        if request_item.get('air_date'):
            self.infolabels['premiered'] = request_item.get('air_date')
            self.infolabels['year'] = request_item.get('air_date')[:4]
        if request_item.get('imdb_id'):
            self.infolabels['imdbnumber'] = request_item.get('imdb_id')
        if request_item.get('runtime'):
            self.infolabels['duration'] = request_item.get('runtime') * 60
        if request_item.get('tagline'):
            self.infolabels['tagline'] = request_item.get('tagline')
        if request_item.get('status'):
            self.infolabels['status'] = request_item.get('status')
        if request_item.get('number_of_episodes'):
            self.infolabels['episode'] = request_item.get('number_of_episodes')
        if request_item.get('number_of_seasons'):
            self.infolabels['season'] = request_item.get('number_of_seasons')
        if request_item.get('episode_number'):
            self.infolabels['episode'] = request_item.get('episode_number')
        if request_item.get('season_number'):
            self.infolabels['season'] = request_item.get('season_number')
        if request_item.get('genres'):
            self.infolabels['genre'] = utils.dict_to_list(request_item.get('genres'), 'name')
        if request_item.get('networks'):
            self.infolabels['studio'] = self.infolabels.setdefault('studio', []) + utils.dict_to_list(request_item.get('networks'), 'name')
        if request_item.get('production_companies'):
            self.infolabels['studio'] = self.infolabels.setdefault('studio', []) + utils.dict_to_list(request_item.get('production_companies'), 'name')
        if request_item.get('production_countries'):
            self.infolabels['country'] = self.infolabels.setdefault('country', []) + utils.dict_to_list(request_item.get('production_countries'), 'name')
        if request_item.get('origin_country'):
            self.infolabels['country'] = self.infolabels.setdefault('country', []) + request_item.get('origin_country')
        if request_item.get('belongs_to_collection'):
            self.infolabels['set'] = request_item.get('belongs_to_collection').get('name')
        if request_item.get('release_dates') and request_item.get('release_dates').get('results'):
            for i in request_item.get('release_dates').get('results'):
                if i.get('iso_3166_1') and i.get('iso_3166_1') == _country:
                    if i.get('release_dates') and i.get('release_dates')[0].get('certification'):
                        self.infolabels['MPAA'] = '{0}{1}'.format(_mpaaprefix, i.get('release_dates')[0].get('certification'))
        if request_item.get('content_ratings') and request_item.get('content_ratings').get('results'):
            for i in request_item.get('content_ratings').get('results'):
                if i.get('iso_3166_1') and i.get('iso_3166_1') == _country and i.get('rating'):
                    self.infolabels['MPAA'] = '{0}{1}'.format(_mpaaprefix, i.get('rating'))

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
            self.infoproperties['set.poster'] = '{0}{1}'.format(IMAGEPATH, request_item.get('belongs_to_collection').get('poster_path'))
            self.infoproperties['set.fanart'] = '{0}{1}'.format(IMAGEPATH, request_item.get('belongs_to_collection').get('backdrop_path'))

    def get_omdb_info(self, request_item):
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
        if request_item.get('credits') or request_item.get('guest_stars'):
            # Cast Members
            cast_list = []
            if request_item.get('guest_stars'):
                cast_list = cast_list + request_item.get('guest_stars')
            if request_item.get('credits') and request_item.get('credits').get('cast'):
                cast_list = cast_list + request_item.get('credits').get('cast')
            if cast_list:
                x = 1
                added_names = []
                for item in sorted(cast_list, key=lambda k: k['order']):
                    if item.get('name') and not item.get('name') in added_names:
                        added_names.append(item.get('name'))  # Add name to temp list to prevent dupes
                        cast_member = {}
                        cast_member['name'] = item.get('name')
                        cast_member['role'] = item.get('character')
                        cast_member['order'] = item.get('order')
                        cast_member['thumbnail'] = '{0}{1}'.format(IMAGEPATH, item.get('profile_path')) if item.get('profile_path') else ''
                        p = 'Cast.{0}.'.format(x)
                        self.infoproperties['{0}name'.format(p)] = cast_member.get('name')
                        self.infoproperties['{0}role'.format(p)] = cast_member.get('role')
                        self.infoproperties['{0}thumb'.format(p)] = cast_member.get('thumbnail')
                        self.cast.append(cast_member)
                        x = x + 1
            # Crew Members
            crew_list = []
            if request_item.get('credits') and request_item.get('credits').get('crew'):
                crew_list = crew_list + request_item.get('credits').get('crew')
            if crew_list:
                x = 1
                for item in crew_list:
                    if item.get('name'):
                        p = 'Crew.{0}.'.format(x)
                        self.infoproperties['{0}name'.format(p)] = item.get('name')
                        self.infoproperties['{0}job'.format(p)] = item.get('job')
                        self.infoproperties['{0}department'.format(p)] = item.get('department')
                        self.infoproperties['{0}thumb'.format(p)] = '{0}{1}'.format(IMAGEPATH, item.get('profile_path')) if item.get('profile_path') else ''
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
        self.dbtype = utils.convert_to_listitem_type(tmdb_type)
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
        self.listitem.setLabel2(self.label2)
        self.listitem.setUniqueIDs({'imdb': self.imdb_id, 'tmdb': self.tmdb_id})
        self.listitem.setInfo(self.library, self.infolabels)
        self.listitem.setProperties(self.infoproperties)
        self.listitem.setArt(self.infoart)
        self.listitem.setCast(self.cast)
        if kwargs.get('info') == 'textviewer':
            self.url = utils.get_url(info='textviewer')
        elif kwargs.get('info') == 'imageviewer':
            self.url = utils.get_url(info='imageviewer', image=self.poster)
        else:
            self.url = utils.get_url(**kwargs)
        xbmcplugin.addDirectoryItem(_handle, self.url, self.listitem, self.is_folder)
