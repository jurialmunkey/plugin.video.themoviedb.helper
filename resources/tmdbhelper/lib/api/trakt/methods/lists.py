def get_list_of_genres(self, trakt_type):
    if trakt_type not in ['movie', 'show']:
        return

    response = self.get_response(f'genres/{trakt_type}s')

    if not response:
        return

    from tmdbhelper.lib.addon.plugin import get_setting, ADDONPATH

    items = []

    for i in response.json():
        item = {}
        item['label'] = i.get('name')
        item['infolabels'] = {}
        item['infoproperties'] = {}
        item['art'] = {
            'icon': f'{ADDONPATH}/resources/icons/trakt/genres.png'
        }
        item['params'] = {
            'info': 'dir_trakt_genre',
            'genre': i.get('slug'),
            'tmdb_type': 'movie' if trakt_type == 'movie' else 'tv'
        }
        item['unique_ids'] = {'slug': i.get('slug')}
        items.append(item)

    def _add_icon(i):
        import xbmcvfs
        slug = i['unique_ids']['slug']
        if not slug:
            return i
        filepath = xbmcvfs.validatePath(xbmcvfs.translatePath(f'{icon_path}/{slug}.png'))
        if not xbmcvfs.exists(filepath):
            return i
        i['art']['icon'] = filepath
        return i

    icon_path = get_setting('trakt_genre_icon_location', 'str')

    if icon_path:
        items = [_add_icon(i) for i in items]

    return items
