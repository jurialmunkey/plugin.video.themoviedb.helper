LIST_ROUTES = {
    'tmdb_directory': {
        'module_name': 'tmdbhelper.lib.sync.providers.tmdb.directories.lists_directory',
        'import_attr': 'ListTMDbDirectory'},
    'tmdb_recommendations': {
        'module_name': 'tmdbhelper.lib.sync.providers.tmdb.directories.lists_authenticated',
        'import_attr': 'ListRecommendations'},
    'tmdb_favorites': {
        'module_name': 'tmdbhelper.lib.sync.providers.tmdb.directories.lists_authenticated',
        'import_attr': 'ListFavourites'},
    'tmdb_rated': {
        'module_name': 'tmdbhelper.lib.sync.providers.tmdb.directories.lists_authenticated',
        'import_attr': 'ListRated'},
    'tmdb_list': {
        'module_name': 'tmdbhelper.lib.sync.providers.tmdb.directories.lists_authenticated',
        'import_attr': 'ListList'},
    'tmdb_lists': {
        'module_name': 'tmdbhelper.lib.sync.providers.tmdb.directories.lists_authenticated',
        'import_attr': 'ListLists'},
}
