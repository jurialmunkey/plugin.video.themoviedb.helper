PREFIX_PATH = 'Path.'
PREFIX_QUERY = 'Query'
PREFIX_CURRENT = 'Path.Current'
PREFIX_ADDPATH = 'Path.To.Add'
PREFIX_POSITION = 'Position'
PREFIX_INSTANCE = 'Instance'
PREFIX_COMMAND = 'Command'
ID_VIDEOINFO = 12003
CONTAINER_ID = 9999


SV_ROUTES = {
    'get_dbitem_movieset_details': {
        'module_name': 'jurialmunkey.jrpcid',
        'import_attr': 'ListGetMovieSetDetails'},
    'get_dbitem_movie_details': {
        'module_name': 'jurialmunkey.jrpcid',
        'import_attr': 'ListGetMovieDetails'},
    'get_dbitem_tvshow_details': {
        'module_name': 'jurialmunkey.jrpcid',
        'import_attr': 'ListGetTVShowDetails'},
    'get_dbitem_season_details': {
        'module_name': 'jurialmunkey.jrpcid',
        'import_attr': 'ListGetSeasonDetails'},
    'get_dbitem_episode_details': {
        'module_name': 'jurialmunkey.jrpcid',
        'import_attr': 'ListGetEpisodeDetails'},
}
