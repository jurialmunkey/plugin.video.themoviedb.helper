from tmdbhelper.lib.items.directories.sync.mapper_currentlywatching import CurrentlyWatchingItemMapper


class NextEpisodeItemMapper(CurrentlyWatchingItemMapper):
    def get_episode_numbers(self):
        if not self.meta.get('next_episode_id'):
            return (1, 1)
        return super().get_episode_numbers()

    def get_infolabels(self):
        infolabels = super().get_infolabels()
        infolabels['tvshowtitle'] = self.meta['title']
        return infolabels
