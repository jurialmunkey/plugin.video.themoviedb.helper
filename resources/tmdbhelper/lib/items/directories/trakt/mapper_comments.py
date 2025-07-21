from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from tmdbhelper.lib.addon.plugin import get_localized
from jurialmunkey.ftools import cached_property


class CommentsItemMapper(ItemMapper):
    @cached_property
    def label(self):
        return self.user.get('name') or self.user.get('username') or ''

    @cached_property
    def user_stats(self):
        return self.meta.get('user_stats') or {}

    @cached_property
    def user(self):
        return self.meta.get('user') or {}

    @cached_property
    def user_ids(self):
        return self.user.get('ids') or {}

    @cached_property
    def rating(self):
        return self.user_stats.get('rating')

    @cached_property
    def play_count(self):
        return self.user_stats.get('play_count')

    @cached_property
    def completed_count(self):
        return self.user_stats.get('completed_count')

    @cached_property
    def premiered(self):
        return self.meta.get('created_at', '')[:10]

    @cached_property
    def rating_score(self):
        rating_score = ', '.join([
            i for i in (
                f'{get_localized(563)} {self.rating}/10' if self.rating else None,
                f'{self.completed_count} watched' if self.completed_count else None,
                f'{self.play_count} play{"s" if self.play_count > 1 else ""}' if self.play_count else None,
            ) if i
        ])

        return rating_score

    @cached_property
    def comment_id(self):
        return self.meta.get('id')

    @cached_property
    def parent_id(self):
        return self.meta.get('parent_id')

    @cached_property
    def user_slug(self):
        return self.user_ids.get('slug')

    @cached_property
    def comment(self):
        comment = '\n'.join([
            i for i in (
                self.meta.get('comment'),
                self.rating_score,
                self.premiered,
            ) if i
        ])
        return comment

    def get_params(self):
        params = {
            'comment_id': self.comment_id,
            'parent_id': self.parent_id,
            'user_slug': self.user_slug,
        }
        return params

    def get_infolabels(self):
        infolabels = {
            'plot': self.comment,
            'premiered': self.premiered,
            'rating': self.rating,
        }
        return infolabels

    def get_infoproperties(self):
        infoproperties = {
            k: v for d in (self.meta, self.user, self.user_stats) for k, v in d.items()
            if v and type(v) not in [list, dict]
        }
        return infoproperties

    def get_unique_ids(self):
        unique_ids = {
            'comment': self.comment_id,
            'parent': self.parent_id,
            'user': self.user_slug,
        }
        return unique_ids
