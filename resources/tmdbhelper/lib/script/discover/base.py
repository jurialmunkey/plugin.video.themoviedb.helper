from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.addon.tmdate import set_timestamp
from jurialmunkey.ftools import cached_property
from jurialmunkey.window import get_property
from xbmcgui import Dialog, WindowXMLDialog, ListItem, INPUT_NUMERIC


class DiscoverItem:
    def __init__(self, label, value, image=None):
        self.label = label
        self.value = value
        self.image = image

    routes = {0: 'label', 1: 'value', 2: 'image'}

    def __getitem__(self, key):
        return getattr(self, self.routes.get(key, key))

    @cached_property
    def label2(self):
        return str(self.value)

    @cached_property
    def icon(self):
        return self.image

    @cached_property
    def art(self):
        return {'icon': self.icon} if self.icon else {}

    @cached_property
    def listitem(self):
        listitem = ListItem(self.label, self.label2)
        listitem.setArt(self.art)
        return listitem


class DiscoverMenu:
    def __init__(self, main):
        self.main = main

    label_affix = None
    paramstring = None
    label = None
    enabled = True
    value = None
    rebuild = False

    @property
    def paramstring(self):
        if not self.value:
            return
        return f'{self.key}={self.value}'

    @property
    def pathlabel(self):
        return f'{self.label_prefix} {self.label}'

    @cached_property
    def listitem(self):
        return ListItem(label=self.listitem_label)

    @cached_property
    def label_prefix(self):
        label_prefix = get_localized(self.label_prefix_localized)
        label_prefix = f'{label_prefix} ({self.label_affix})' if self.label_affix else label_prefix
        return label_prefix

    @property
    def listitem_label(self):
        return f'{self.label_prefix}: {self.label}' if self.label else self.label_prefix

    def menu_rebuild(self):
        if not self.rebuild:
            return
        self.main.rebuild_menu(self.__class__.__name__)


class DiscoverList(DiscoverMenu):
    idx = None
    key = 'info'
    label_prefix_localized = 535
    use_details = False
    default_idx = None

    @property
    def route(self):
        if self.idx is None:
            return
        return self.routes[self.idx]

    @property
    def label(self):
        if not self.route:
            return
        return self.route.label

    @property
    def value(self):
        if not self.route:
            return
        return self.route.value

    @cached_property
    def routes(self):
        return self.get_routes()

    def get_routes(self):
        return ()

    def reset_routes(self):
        self.routes = self.get_routes()

    @property
    def dialog_select(self):
        return Dialog().select

    @property
    def preselect(self):
        return self.idx if self.idx is not None else -1

    def load_value(self, value):
        self.idx = next((x for x, i in enumerate(self.routes) if i.value == value), None)

    @property
    def menu_items(self):
        if not self.use_details:
            return [i.label for i in self.routes]
        return [i.listitem for i in self.routes]

    def menu(self):
        x = self.dialog_select(self.listitem_label, self.menu_items, preselect=self.preselect, useDetails=self.use_details)
        self.idx = x if x != -1 else self.default_idx
        self.listitem.setLabel(self.listitem_label)
        self.menu_rebuild()


class DiscoverMulti(DiscoverList):

    separator = '%2C'

    @property
    def dialog_select(self):
        return Dialog().multiselect

    @property
    def route(self):
        if not self.idx:
            return
        return [self.routes[x] for x in self.idx]

    @property
    def label(self):
        if not self.route:
            return
        label = ' AND ' if self.separator == '%2C' else ' OR '
        label = label.join((i.label for i in self.route))
        return label

    @property
    def value(self):
        if not self.route:
            return
        return self.separator.join((f'{i.value}' for i in self.route))

    @property
    def preselect(self):
        return self.idx or []

    @property
    def has_multiples(self):
        return bool(self.idx and len(self.idx) > 1)

    def get_separator(self):
        if not self.has_multiples:
            return
        x = Dialog().select(get_localized(32107), (get_localized(32110), get_localized(32109)))
        if x == -1:
            return
        return '%7C' if x == 1 else '%2C'

    def set_separator(self, value):
        self.separator = value or self.separator


class DiscoverQuery(DiscoverMenu):
    key = 'query'
    label_prefix_localized = 32153
    label = None

    def load_value(self, value):
        self.label = value

    @property
    def query_header(self):
        return get_localized(32044)

    @property
    def value(self):
        return self.label

    def get_query(self):
        return Dialog().input(self.query_header, defaultt=self.value or '')

    def menu(self):
        self.label = self.get_query()
        self.listitem.setLabel(self.listitem_label)
        self.menu_rebuild()


class DiscoverNumeric(DiscoverQuery):
    def get_query(self):
        return Dialog().input(self.query_header, defaultt=self.value or '', type=INPUT_NUMERIC)


class DiscoverRuntimes(DiscoverMenu):
    value_a = None
    value_z = None

    key = 'runtimes'
    label_prefix_localized = 2050

    @property
    def input_label(self):
        return get_localized(12391)

    @property
    def label(self):
        if not self.value_a:
            return
        if not self.value_z:
            return f'{self.value_a}'
        if self.value_a == self.value_z:
            return f'{self.value_a}'
        return f'{self.value_a}-{self.value_z}'

    @property
    def value(self):
        return self.label

    def menu(self):
        self.value_a = Dialog().input(f'{self.input_label} [ > or = ]', type=INPUT_NUMERIC, defaultt=f'{self.value_a}' if self.value_a else '')
        self.value_z = Dialog().input(f'{self.input_label} [ < or = ]', type=INPUT_NUMERIC, defaultt=f'{self.value_z}' if self.value_z else '')
        self.listitem.setLabel(self.listitem_label)
        self.menu_rebuild()


class DiscoverYears(DiscoverRuntimes):
    key = 'years'
    label_prefix_localized = 652

    base_range_start = 1900
    base_range_end = 2030
    base_range_increment = 10
    base_range_reverse = True

    @property
    def base_range(self):
        return (self.base_range_start, self.base_range_end, self.base_range_increment)

    @property
    def base_values(self):
        return sorted(tuple(range(*self.base_range)), reverse=self.base_range_reverse)

    @property
    def base_label(self):
        return get_localized(32157)

    @property
    def input_label(self):
        return get_localized(32279)

    @staticmethod
    def select_options(vals):
        return [f'{i}' for i in vals]

    def select_base_value(self, *label_affixes, lower_limit=0):
        vals = tuple((i for i in self.base_values if i > lower_limit))
        if not vals:
            return
        head = ' '.join((self.input_label, *label_affixes))
        opts = self.select_options(vals)
        indx = Dialog().select(head, opts)
        return vals[indx] if indx != -1 else None

    def select_value(self, *label_affixes, lower_limit=0):
        base = self.select_base_value(self.base_label, *label_affixes, lower_limit=lower_limit - 9)
        if base is None:
            return
        vals = sorted(tuple(range(base, base + self.base_range_increment)), reverse=self.base_range_reverse)
        vals = tuple((i for i in vals if i > lower_limit))
        if not vals:
            return
        head = ' '.join((self.input_label, *label_affixes))
        opts = self.select_options(vals)
        indx = Dialog().select(head, opts)
        return vals[indx] if indx != -1 else None

    def menu(self):
        self.value_a = self.select_value('[ > or = ]')
        self.value_z = self.select_value(f'{self.value_a}', '[ < or = ]', lower_limit=self.value_a) if self.value_a else None
        self.listitem.setLabel(self.listitem_label)
        self.menu_rebuild()


class DiscoverYear(DiscoverYears):
    value = None

    @property
    def label(self):
        return str(self.value) if self.value is not None else ''

    def menu(self):
        self.value = self.select_value()
        self.listitem.setLabel(self.listitem_label)
        self.menu_rebuild()


class DiscoverRatings(DiscoverYears):
    key = 'ratings'
    label_prefix_localized = 32028

    base_range_start = 0
    base_range_end = 101
    base_range_increment = 5

    @property
    def input_label(self):
        return f'{get_localized(32028)} (%/100)'

    def select_value(self, *label_affixes, lower_limit=0):
        return self.select_base_value(*label_affixes, lower_limit=lower_limit)


class DiscoverSave(DiscoverMenu):

    label_prefix_localized = 190

    def save(self):
        from tmdbhelper.lib.script.method.nodes import TMDbNode
        make_node = TMDbNode(name=self.main.name, path=self.main.path, icon=self.main.icon)
        make_node.notification = False
        make_node.overwrite = True
        make_node.file = self.main.file
        make_node.add(insert=0)

    def menu(self):
        if self.main.name:
            self.save()
            self.main.data['path'] = self.main.path
            self.main.data['file'] = self.main.file
            self.main.data['name'] = self.main.name
            self.main.data['icon'] = self.main.icon
        self.main.close()


class DiscoverReset(DiscoverMenu):

    label_prefix_localized = 13007

    def menu(self):
        self.main.routes_dict = self.main.get_routes_dict()
        self.main.rebuild_menu()


class DiscoverMain(WindowXMLDialog):

    ACTION_SELECT = (7, 100, )
    ACTION_CLOSEWINDOW = (9, 10, 92, 216, 247, 257, 275, 61467, 61448,)
    file = ''
    label = ''
    icon = ''
    winprop = ''
    base_params = ()

    @cached_property
    def name(self):
        return Dialog().input(get_localized(32241), defaultt=self.defaultt)

    @cached_property
    def data(self):
        return {}

    @property
    def path(self):
        path = '&'.join((*self.base_params, *tuple((i.paramstring for i in self.routes if i.paramstring))))
        path = 'plugin://plugin.video.themoviedb.helper/?' + path
        return path

    @property
    def defaultt(self):
        from tmdbhelper.lib.files.futils import validify_filename
        defaultt = ', '.join((i.pathlabel for i in self.routes if i.label and i.paramstring))
        defaultt = validify_filename(defaultt)
        return ' '.join(defaultt.split())

    @cached_property
    def routes_dict(self):
        return self.get_routes_dict()

    def update_winprop(self):
        if not self.winprop:
            return
        get_property(self.winprop, set_property=self.path)
        get_property(f'{self.winprop}.name', set_property=f'{self.defaultt}')
        get_property(f'{self.winprop}.paramstring', set_property='&'.join((i.paramstring for i in self.routes if i.paramstring)))
        get_property(f'{self.winprop}.reload', set_property=f'{set_timestamp(0, True)}')

    def get_routes_dict(self):
        return {}

    @property
    def routes(self):
        return tuple((i for i in self.routes_dict.values() if i.enabled))

    def route_index(self, class_name):
        return next((x for x, i in enumerate(self.routes) if i.__class__.__name__ == class_name), None)

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    def onAction(self, action):
        action_id = action.getId()
        if action_id in self.ACTION_CLOSEWINDOW:
            return self.on_autosave()
        if action_id in self.ACTION_SELECT:
            return self.click()

    def click(self):
        focus_id = self.getFocusId()
        if focus_id == 3:
            return self.on_action()
        if focus_id == 7:
            return self.close()
        if focus_id == 8:
            return self.on_reset()
        if focus_id == 5:
            return self.on_save()

    def on_action(self):
        x = self.list_control.getSelectedPosition()
        self.routes[x].menu()
        self.update_winprop()

    def on_reset(self):
        value = self.routes_dict['reset'].menu()
        self.update_winprop()
        return value

    def on_save(self):
        value = self.routes_dict['save'].menu()
        self.update_winprop()
        return value

    def on_autosave(self):
        self.name = self.defaultt
        return self.on_save()

    @property
    def list_control(self):
        return self.getControl(3)

    def load_values(self, **kwargs):
        load_values = tuple((
            (k.replace('.', '_'), v.replace(',', '%2C').replace('|', '%7C'))
            for k, v in kwargs.items() if k and v
        ))
        load_values = tuple((
            (k, v) for k, v in load_values
            if k in self.routes_dict
        ))
        for k, v in load_values:
            self.routes_dict[k].load_value(v)

    def rebuild_menu(self, select_class=None):
        for i in self.routes:
            try:
                i.reset_routes()
            except AttributeError:
                pass
        self.build_menu(select_class)

    def onInit(self):
        self.build_menu()
        self.getControl(1).setLabel(self.label)
        self.getControl(5).setLabel(get_localized(190))
        self.getControl(6).setVisible(False)
        self.getControl(7).setLabel(get_localized(15067))
        self.getControl(8).setLabel(get_localized(13007))

    def build_menu(self, select_class=None):
        self.list_control.reset()
        self.list_control.addItems([i.listitem for i in self.routes])
        self.setFocus(self.list_control)
        self.list_control.selectItem(self.route_index(select_class) or 0) if select_class is not None else None
        self.update_winprop()
