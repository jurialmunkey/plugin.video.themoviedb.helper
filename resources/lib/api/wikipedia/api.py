import re
import xbmcgui
from bs4 import BeautifulSoup
from resources.lib.api.request import RequestAPI
from resources.lib.addon.dialog import BusyDialog
from resources.lib.addon.thread import ParallelThread


WIKI_NAME_ID = 9901
WIKI_LIST_ID = 9902
WIKI_TEXT_ID = 9903
ACTION_CLOSEWINDOW = (9, 10, 92, 216, 247, 257, 275, 61467, 61448,)
ACTION_MOVEMENT = (1, 2, 3, 4, )


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

    def get_section(self, title, section_index):
        params = {
            'action': 'parse', 'page': title, 'format': 'json', 'prop': 'text',
            'disabletoc': True, 'section': section_index, 'redirects': ''}
        return self.get_request_lc(**params)

    def get_all_sections(self, title):
        sections = self.get_sections(title)
        sections = [{'line': 'Overview', 'index': '0', 'number': '0'}] + sections
        return sections

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
        with BusyDialog():
            self._title = self._wiki.get_match(self._query, self._tmdb_type)
            self._overview = self._wiki.parse_text(self._wiki.get_section(self._title, '0'))
            self._sections = self._wiki.get_all_sections(self._title)

    def onInit(self):
        self._gui_name = self.getControl(WIKI_NAME_ID)
        self._gui_list = self.getControl(WIKI_LIST_ID)
        self._gui_text = self.getControl(WIKI_TEXT_ID)
        if not self._title:
            xbmcgui.Dialog().ok('Wikipedia', 'No search results')
            self.close()
        self._gui_name.setLabel(f'{self._title}')
        self._gui_text.setText(f'{self._overview}')
        self.set_sections()
        # self._thread = Thread(target=self.set_sections)
        # self._thread.start()

    def onAction(self, action):
        _action_id = action.getId()
        if _action_id in ACTION_CLOSEWINDOW:
            return self.close()
        if _action_id in ACTION_MOVEMENT:
            return self.do_scroll()

    def do_scroll(self):
        if self.getFocusId() != WIKI_LIST_ID:
            return
        x = self._gui_list.getSelectedPosition()
        try:
            text = self._index[x]
        except (TypeError, AttributeError, KeyError, IndexError):
            return
        self._gui_text.setText(text)

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
