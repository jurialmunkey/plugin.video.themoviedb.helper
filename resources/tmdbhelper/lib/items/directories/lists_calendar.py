from jurialmunkey.ftools import cached_property


class CalendarItemCollect:

    def __init__(self):
        self.items = []

    def append(self, item):
        self.items.append(item)

    @staticmethod
    def get_formatted_label(item):
        return f"{item['infolabels']['season']}x{item['infolabels']['episode']:02}"

    @cached_property
    def tmdb_id(self):
        return self.items[0]['unique_ids']['tvshow.tmdb']

    @cached_property
    def stacked_count(self):
        return f'{len(self.items)}'

    @cached_property
    def stacked_episodes(self):
        return ', '.join(self.stacked_episodes_list)

    @cached_property
    def stacked_episodes_list(self):
        return [
            self.get_formatted_label(i)
            for i in self.items
        ]

    @cached_property
    def stacked_episodes_with_titles_list(self):
        return [
            f'{self.get_formatted_label(i)} - {i["label"]}'
            for i in self.items
        ]

    @cached_property
    def infoproperties(self):
        return {
            'stacked_count': self.stacked_count,
            'stacked_episodes': self.stacked_episodes,
            'stacked_labels': ', '.join(self.stacked_episodes_with_titles_list),
            'stacked_titles': ', '.join([i['label'] for i in self.items]),
            'stacked_first': self.stacked_episodes_list[0],
            'stacked_last': self.stacked_episodes_list[-1],
            'stacked_first_episode': self.items[0]['infolabels']['episode'],
            'stacked_last_episode': self.items[-1]['infolabels']['episode'],
            'stacked_first_season': self.items[0]['infolabels']['season'],
            'stacked_last_season': self.items[-1]['infolabels']['season'],
            'stacked_first_title': self.items[0]['label'],
            'stacked_last_title': self.items[-1]['label'],
            'label_affix': f"{self.stacked_episodes_list[0]} - {self.stacked_episodes_list[-1]}",
            'label_override': self.label
        }

    @cached_property
    def params(self):
        return {
            'info': 'specified_episodes',
            'tmdb_id': self.tmdb_id,
            'tmdb_type': 'tv',
            'episodes': '/'.join(self.stacked_episodes_list),
        }

    @cached_property
    def infolabels(self):
        return {
            'title': self.label,
            'mediatype': 'tvshow',
        }

    @cached_property
    def label(self):
        return self.items[0]['infolabels']['tvshowtitle']

    @cached_property
    def item(self):
        if not self.items:
            return {}

        if len(self.items) == 1:
            return self.items[0]

        return {
            'params': self.params,
            'label': self.label,
            'infolabels': self.infolabels,
            'infoproperties': self.infoproperties,
            'unique_ids': self.items[0]['unique_ids'],
        }


class CalendarItemStacker:

    prev_item_id = None
    next_item_id = None

    def __init__(self, source_items):
        self.source_items = source_items

    def get_item_id(self, item):
        try:
            item_id = (
                item['unique_ids']['tvshow.slug'],
                item['infolabels']['premiered'],
            )
            return f'{item_id}'
        except (KeyError, TypeError):
            return

    @cached_property
    def items(self):
        items = []

        for i in self.source_items:

            if not items or self.get_item_id(items[-1].items[0]) != self.get_item_id(i):
                items.append(CalendarItemCollect())

            items[-1].append(i)

        return [i.item for i in items]
