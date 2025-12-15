# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from tmdbhelper.lib.files.futils import get_files_in_folder, read_file, dumps_to_file, delete_file
from tmdbhelper.lib.addon.consts import NODE_BASEDIR
from tmdbhelper.lib.addon.plugin import get_infolabel, get_localized, executebuiltin
from jurialmunkey.ftools import cached_property
from json import loads, JSONDecodeError
from xbmcgui import Dialog


class TMDbNodeOptionAdd:
    def __init__(self, file):
        self.file = file

    @cached_property
    def label(self):
        return self.file[:-5] if self.file.endswith('.json') else self.file


class TMDbNodeOptionNew:
    @cached_property
    def label(self):
        return get_localized(32495)

    @cached_property
    def file(self):
        file = Dialog().input(get_localized(551))
        return f'{file}.json' if file else None


class TMDbNode:

    overwrite = False
    notification = True
    allow_listitem = True

    def __init__(self, name=None, icon=None, path=None):
        self.name = name or self.name
        self.icon = icon or self.icon
        self.path = path or self.path

    @cached_property
    def name(self):
        if not self.allow_listitem:
            return ''
        return get_infolabel('Container.ListItem.Label') or ''

    @cached_property
    def icon(self):
        if not self.allow_listitem:
            return ''
        return get_infolabel('Container.ListItem.Icon') or ''

    @cached_property
    def path(self):
        if not self.allow_listitem:
            return ''
        return get_infolabel('Container.ListItem.FolderPath') or ''

    @property
    def item(self):
        return {
            'name': self.name,
            'icon': self.icon,
            'path': self.path
        }

    @cached_property
    def files(self):
        return get_files_in_folder(NODE_BASEDIR, r'.*\.json')

    @cached_property
    def options(self):
        options = [TMDbNodeOptionAdd(f) for f in self.files]
        options.append(TMDbNodeOptionNew())
        return options

    @cached_property
    def file(self):
        x = Dialog().select(get_localized(32504).format(self.name), [i.label for i in self.options])
        return self.options[x].file if x != -1 else None

    @cached_property
    def meta(self):
        if not self.file:
            return
        try:
            meta = loads(read_file(NODE_BASEDIR + self.file))
        except JSONDecodeError:
            meta = None
        meta = meta or {
            'name': self.file[:-5] if self.file.endswith('.json') else self.file,
            'icon': '',
            'list': [],
        }
        return meta

    def notify(self, message):
        if not self.notification:
            return
        Dialog().ok(self.name, message)

    def add(self, insert=None):
        if not self.meta:
            return

        # Check we don't already have an item with that name in the node
        if any(bool(i['name'] == self.item['name']) for i in self.meta['list']):
            self.notify(get_localized(32492).format(self.name, self.file))
            if not self.overwrite:
                return
            self.remove(refresh=False)

        # Add item to node
        self.meta['list'].append(self.item) if insert is None else self.meta['list'].insert(insert, self.item)

        # Save node
        dumps_to_file(self.meta, NODE_BASEDIR, self.file, join_addon_data=False)
        self.notify(get_localized(32494).format(self.name, self.file))

    def remove(self, refresh=True):
        if not self.meta:
            return

        remove = [x for x, i in enumerate(self.meta['list']) if i['name'] == self.name]

        if not remove:
            return

        for x in sorted(remove, reverse=True):
            del self.meta['list'][x]

        if self.meta['list']:
            dumps_to_file(self.meta, NODE_BASEDIR, self.file, join_addon_data=False)
        else:  # If there are no items left in the list then delete the whole thing
            delete_file(NODE_BASEDIR, self.file, join_addon_data=False)

        self.notify(get_localized(32493).format(self.name, self.file))

        if not refresh:
            return

        if self.meta['list']:
            executebuiltin('Container.Refresh')
        else:  # If there are no items left in the list then we'll get kicked out so go back to base dir
            executebuiltin('Container.Update(plugin://plugin.video.themoviedb.helper/?info=dir_custom_node&tmdb_type=None)')


def make_node(name=None, icon=None, path=None, file=None, **kwargs):
    make_node = TMDbNode(name=name, icon=icon, path=path)
    make_node.file = file or make_node.file
    make_node.add()


def remove_node(name=None, icon=None, path=None, file=None, **kwargs):
    remove_node = TMDbNode(name=name, icon=icon, path=path)
    remove_node.file = file
    remove_node.remove()
