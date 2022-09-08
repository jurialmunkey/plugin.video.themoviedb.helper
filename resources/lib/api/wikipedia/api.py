import re
import xbmcgui
from bs4 import BeautifulSoup
from resources.lib.api.request import RequestAPI
from resources.lib.addon.dialog import BusyDialog
from resources.lib.addon.thread import ParallelThread


WIKI_NAME_ID = 9901
WIKI_LIST_ID = 9902
WIKI_TEXT_ID = 9903
WIKI_ATTR_ID = 9904
WIKI_CCIM_ID = 9905
WIKI_ATTRIBUTION = 'Text from Wikipedia under CC BY-SA 3.0 license.\n{}'
WIKI_CCBYSA_IMG = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/CC_BY-SA_icon.svg/320px-CC_BY-SA_icon.svg.png'

ACTION_CLOSEWINDOW = (9, 10, 92, 216, 247, 257, 275, 61467, 61448,)
ACTION_MOVEMENT = (1, 2, 3, 4, )
ACTION_SELECT = (7, )


AFFIXES = {
    'tv': {
        'regex': r'\(TV series\)$',
        'affix': 'television series'
    },
    'movie': {
        'regex': r'\(Film\)$',
        'affix': 'film'
    },
    'person': {
        'regex': r'\(.*\)$',
        'affix': 'born'
    },
}


class WikipediaAPI(RequestAPI):
    def __init__(self):
        super(WikipediaAPI, self).__init__(
            req_api_name='Wikipedia',
            req_api_url='https://en.wikipedia.org/w/api.php')

    def get_search(self, query, affix=None):
        params = {
            'action': 'query', 'format': 'json', 'list': 'search', 'utf8': 1,
            'srsearch': f'{query} {affix}' if affix else query}
        return self.get_request_lc(**params)

    def get_match(self, query, tmdb_type=None, match=''):
        affixes = AFFIXES.get(tmdb_type, {})
        # regex = affixes.get('regex')
        affix = affixes.get('affix')
        _data = self.get_search(query, affix)
        items = [i['title'] for i in _data['query']['search']]
        x = xbmcgui.Dialog().select('Wikipedia', items)
        if x == -1:
            return
        return items[x]

        # best_title = None
        # for i in data['query']['search']:
        #     if regex and i['title'].split(' (')[0] == query and re.match(regex, i['title']):
        #         return i['title']
        #     if not best_title and i['title'] == query and match in i['snippet']:
        #         best_title = i['title']
        #     if not best_title and match in i['snippet']:
        #         best_title = i['title']
        # return best_title

    def get_extract(self, title):
        params = {
            'action': 'query', 'format': 'json', 'titles': title, 'prop': 'extracts',
            'exintro': True, 'explaintext': True}
        return self.get_request_lc(**params)

    def get_sections(self, title):
        params = {
            'action': 'parse', 'page': title, 'format': 'json', 'prop': 'sections',
            'disabletoc': True, 'redirects': ''}
        try:
            return self.get_request_lc(**params)['parse']['sections']
        except (KeyError, AttributeError, TypeError):
            return []

    def get_fullurl(self, title):
        params = {'action': 'query', 'format': 'json', 'titles': title, 'prop': 'info', 'inprop': 'url'}
        try:
            data = self.get_request_lc(**params)['query']['pages']
            data = data[next(iter(data))]['fullurl']
        except (KeyError, AttributeError, TypeError):
            return ''
        return data

    def get_section(self, title, section_index):
        params = {
            'action': 'parse', 'page': title, 'format': 'json', 'prop': 'text',
            'disabletoc': True, 'section': section_index, 'redirects': ''}
        return self.get_request_lc(**params)

    def get_all_sections(self, title):
        sections = self.get_sections(title)
        sections = [{'line': 'Overview', 'index': '0', 'number': '0'}] + sections
        return sections

    def parse_links(self, data):
        raw_html = data['parse']['text']['*']
        soup = BeautifulSoup(raw_html, 'html.parser')
        links = [
            i['title'] for i in soup.find_all('a')
            if i.get('title')
            and i.get('href', '').startswith('/wiki/')
            and not i['title'].startswith('Help:')
            and not i['title'].startswith('Special:')
            and not i.get('href', '').startswith('/wiki/File:')]
        return links

    def parse_text(self, data):
        raw_html = data['parse']['text']['*']
        soup = BeautifulSoup(raw_html, 'html.parser')
        text = [p.get_text() for p in soup.find_all('p')]

        # tabl = [p.get_text() for p in soup.find_all('tr')]
        # tabl = [i.replace('\n', ' ') for i in tabl if i]
        # text += tabl

        text += [p.get_text() for p in soup.find_all('li')]
        text = [i for i in text if 'Cite error' not in i and not i.startswith('^')]

        text = '\n'.join(text)
        text = re.sub(r'\[[0-9]*\]', '', text)
        text = re.sub(r'^(\n)*', '', text)
        return text


class WikipediaGUI(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self._index = []
        self._query = kwargs.get('query')
        self._tmdb_type = kwargs.get('tmdb_type')
        self._wiki = WikipediaAPI()
        self._title = ''
        self._history = []
        with BusyDialog():
            self.do_setup()

    def do_setup(self, title=None):
        self._title = title or self._wiki.get_match(self._query, self._tmdb_type)
        if not self._title:
            return
        self._overview = self._wiki.parse_text(self._wiki.get_section(self._title, '0'))
        self._sections = self._wiki.get_all_sections(self._title)
        self._fullurl = self._wiki.get_fullurl(self._title)

    def do_init(self):
        self._gui_name.setLabel(f'{self._title}')
        self._gui_text.setText(f'{self._overview}')
        self._gui_attr.setText(WIKI_ATTRIBUTION.format(self._fullurl))
        self._gui_ccim.setImage(WIKI_CCBYSA_IMG)
        self.set_sections()

    def onInit(self):
        self._gui_name = self.getControl(WIKI_NAME_ID)
        self._gui_list = self.getControl(WIKI_LIST_ID)
        self._gui_text = self.getControl(WIKI_TEXT_ID)
        self._gui_attr = self.getControl(WIKI_ATTR_ID)
        self._gui_ccim = self.getControl(WIKI_CCIM_ID)
        if not self._title:
            self.close()
        self.do_init()

    def onAction(self, action):
        _action_id = action.getId()
        if _action_id in ACTION_CLOSEWINDOW:
            return self.do_close()
        if _action_id in ACTION_MOVEMENT:
            return self.do_scroll()
        if _action_id in ACTION_SELECT:
            return self.do_click()

    def do_close(self):
        if not self._history:  # No history so close
            return self.close()
        with BusyDialog():  # History so go back instead
            self.do_setup(self._history.pop())
        self.do_init()

    def do_scroll(self):
        if self.getFocusId() != WIKI_LIST_ID:
            return
        x = self._gui_list.getSelectedPosition()
        try:
            text = self._index[x]
            name = self._sections[x]['line']
        except (TypeError, AttributeError, KeyError, IndexError):
            return
        self._gui_text.setText(f'[B]{name}[/B]\n{text}')

    def do_click(self):
        if self.getFocusId() != WIKI_LIST_ID:
            return
        x = self._gui_list.getSelectedPosition()
        links = self._wiki.parse_links(self._wiki.get_section(self._title, f'{x}'))
        if not links:
            return
        links = [i for i in set(links)]
        x = xbmcgui.Dialog().select('Links', links)
        if x == -1:
            return
        self._history.append(self._title)
        with BusyDialog():
            self.do_setup(links[x])
        self.do_init()

    def set_sections(self):
        self._index = []
        self._exit = False
        itms = []
        for section in self._sections:
            if self._exit:
                break
            name = section.get('line')
            indx = section.get('index')
            name = re.sub(r'<.*>', '', name)
            numb = section.get('number')
            name = f"{'    ' if '.' in numb else ''}{numb} {name}"
            if not name or not indx:
                continue
            itms.append((name, indx,))
        self._gui_list.reset()
        self._gui_list.addItems([xbmcgui.ListItem(i) for i, j in itms])

        def _threaditem(i):
            indx = i[1]
            text = self._wiki.parse_text(self._wiki.get_section(self._title, indx))
            text = text or '*** Unable to parse information in this section ***'
            return text

        with ParallelThread(itms, _threaditem) as pt:
            item_queue = pt.queue
        self._index = [i for i in item_queue]


def do_wikipedia_gui(wikipedia, tmdb_type=None, **kwargs):
    from resources.lib.addon.plugin import ADDONPATH
    ui = WikipediaGUI(
        'script-tmdbhelper-wikipedia.xml', ADDONPATH, 'default', '1080i',
        query=wikipedia, tmdb_type=tmdb_type)
    ui.doModal()
    del ui
