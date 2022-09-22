import re
import xbmcgui
from bs4 import BeautifulSoup
from resources.lib.api.request import RequestAPI
from resources.lib.addon.dialog import BusyDialog
from resources.lib.addon.thread import ParallelThread
from resources.lib.addon.plugin import get_language


WIKI_SCRL_ID = 61
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

WIKI_LANGUAGE = {'it': 'it', 'de': 'de', 'en': 'en', 'fr': 'fr', 'es': 'es'}
DEFAULT_WIKI_LANGUAGE = 'en'

WIKI_TAG_LINK = '[COLOR=BF55DDFF]{}[/COLOR]'
WIKI_TAG_BOLD = '[B]{}[/B]'
WIKI_TAG_EMPH = '[LIGHT][I]{} [/I][/LIGHT]'
WIKI_TAG_SUPS = '[LIGHT]{}[/LIGHT]'


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


class WikimediaAPI(RequestAPI):
    def __init__(self):
        super(WikimediaAPI, self).__init__(
            req_api_name='Wikimedia',
            req_api_url='https://commons.m.wikimedia.org/w/api.php')

    def get_titles(self, query):
        params = {
            'action': 'query', 'list': 'search', 'format': 'json',
            'srsearch': f'File: {query}'}
        data = self.get_request_lc(**params)
        if not data:
            return
        return [i['title'] for i in data['query']['search'] if i.get('title')]

    def get_images(self, titles):
        params = {
            'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'titles': '|'.join(titles),
            'iiprop': 'timestamp|user|userid|comment|canonicaltitle|url|size|dimensions|sha1|mime|thumbmime|mediatype|bitdepth'}
        return self.get_request_lc(**params)

    def get_backdrop(self, query):
        data = self.get_images(self.get_titles(query))
        for k, v in data['query']['pages'].items():
            for i in v.get('imageinfo', []):
                if i.get('width', 0) < 1280:
                    continue
                if i.get('width', 0) < i.get('height', 0):
                    continue
                if i.get('mime') != "image/jpeg":
                    continue
                if i.get('url'):
                    return i.get('url')


class WikipediaAPI(RequestAPI):
    def __init__(self):
        lang = get_language()[:2]
        lang = WIKI_LANGUAGE.get(lang) or DEFAULT_WIKI_LANGUAGE

        super(WikipediaAPI, self).__init__(
            req_api_name='Wikipedia' if lang == DEFAULT_WIKI_LANGUAGE else f'Wikipedia_{lang}',
            req_api_url=f'https://{lang}.wikipedia.org/w/api.php')

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
            'disabletoc': True, 'section': section_index, 'redirects': '',
            'disablelimitreport': True,
            'disableeditsection': True,
            'mobileformat': True}
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
            and not i['title'].startswith('Wikipedia:')
            and not i['title'].startswith('Template:')
            and not i['title'].startswith('Category:')
            and not i.get('href', '').startswith('/wiki/File:')]
        return links

    def parse_image(self, data):
        raw_html = data['parse']['text']['*']
        soup = BeautifulSoup(raw_html, 'html.parser')
        links = [i for i in soup.find_all('img') if i.get('src')]
        return links

    def parse_text(self, data):
        raw_html = data['parse']['text']['*']
        soup = BeautifulSoup(raw_html, 'html.parser')
        # return soup.prettify()
        text = []

        def _parse_table(p):
            for c in p.children:
                if c.name in ['style']:
                    continue
                if c.name and any(x in ['mw-references-wrap', 'references-text', 'mw-editsection'] for x in c.get('class', [])):
                    continue
                # if c.name:
                #     text.append(f'<{c.name}>')
                if c.name in ['div', 'br']:
                    text.append(' ')
                elif c.name in ['p', 'table', 'tr', 'li']:
                    text.append('\n\n')
                # elif c.name in ['br']:
                #     text.append('\n')
                if c.name == 'img' and c.get('title'):
                    text.append(f'{c["title"]}')
                    continue
                if c.string:
                    if c.string.startswith('^'):
                        continue
                    t = c.string.replace('\n', ' ')
                    if c.name in ['th', 'td']:
                        t = f'{t} '
                    if c.name and 'mw-headline' in c.get('class', ''):
                        t = WIKI_TAG_BOLD.format(t)
                    elif c.name in ['th', 'h2', 'b', 'h3', 'h1', 'h4']:
                        t = WIKI_TAG_BOLD.format(t)
                    elif c.name in ['i', 'em']:
                        t = WIKI_TAG_EMPH.format(t)
                    elif c.name in ['sup']:
                        t = WIKI_TAG_SUPS.format(t)
                    elif c.name in ['u', 'a']:
                        t = WIKI_TAG_LINK.format(t)
                    elif c.name in ['li']:
                        t = '* {}'.format(t)
                    text.append(f'{t}')
                    continue
                if c.children:
                    _parse_table(c)
                    continue

        _parse_table(soup)

        text = ''.join(text)
        text = re.sub(r'\[[0-9]*\]', '', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'( *\n){3,}', '\n\n', text)
        text = re.sub(r'^(\n)+', '', text)
        text = re.sub(r'^ +', '', text)
        text = re.sub(r'\n +', '\n', text)
        return text


class WikipediaGUI(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self._index = []
        self._query = kwargs.get('query')
        self._tmdb_type = kwargs.get('tmdb_type')
        self._wiki = WikipediaAPI()
        self._wikimedia = WikimediaAPI()
        self._backdrop = ''
        self._title = ''
        self._overview_img = ''
        self._history = []
        with BusyDialog():
            self.do_setup()

    def do_setup(self, title=None):
        self._title = title or self._wiki.get_match(self._query, self._tmdb_type)
        if not self._title:
            return
        self._name = title or self._title
        self._overview = self._wiki.parse_text(self._wiki.get_section(self._title, '0'))
        self._sections = self._wiki.get_all_sections(self._title)
        self._fullurl = self._wiki.get_fullurl(self._title)

    def do_init(self):
        xbmcgui.Window(10000).clearProperty('TMDbHelper.Wikipedia.Backdrop')
        self.clearProperty('Backdrop')
        self._gui_name.setLabel(f'{self._title}')
        self._gui_text.setText(f'{self._overview}')
        self._gui_attr.setText(WIKI_ATTRIBUTION.format(self._fullurl))
        self._gui_ccim.setImage(WIKI_CCBYSA_IMG)
        self.clearProperty('Image')
        self.set_sections()
        self.setFocusId(WIKI_LIST_ID)
        self.set_section(0)
        self._overview_img = self.get_image(0)
        self._backdrop = self._wikimedia.get_backdrop(self._name) or ''
        if self._backdrop:
            xbmcgui.Window(10000).setProperty('TMDbHelper.Wikipedia.Backdrop', self._backdrop)
            self.setProperty('Backdrop', self._backdrop)

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
        if self.getFocusId() == WIKI_SCRL_ID:
            return self.setFocusId(WIKI_LIST_ID)
        if not self._history:  # No history so close
            return self.close()
        with BusyDialog():  # History so go back instead
            self.do_setup(self._history.pop())
        self.do_init()

    def do_scroll(self):
        if self.getFocusId() != WIKI_LIST_ID:
            return
        self.set_section(self._gui_list.getSelectedPosition())

    def do_click(self):
        # if self.getFocusId() != WIKI_LIST_ID:
        #     return
        x = self._gui_list.getSelectedPosition()
        links = self._wiki.parse_links(self._wiki.get_section(self._title, f'{x}'))
        if not links:
            return
        links = list(dict.fromkeys(links))
        x = xbmcgui.Dialog().select('Links', links)
        if x == -1:
            return
        self._history.append(self._title)
        with BusyDialog():
            self.do_setup(links[x])
        self.do_init()

    def get_image(self, x):
        try:
            imgs = self._wiki.parse_image(self._wiki.get_section(self._title, f'{x}'))
        except (TypeError, AttributeError, KeyError, IndexError):
            return
        if not imgs:
            return
        for img in imgs:
            if int(img.get('width', 100)) < 32:
                continue
            if int(img.get('height', 100)) < 32:
                continue
            return img

    def set_image(self, img=None):
        img = img or self._overview_img
        self.setProperty('Image', f'https:{img.get("src")}')
        self.setProperty('ImageText', f'{img.get("title") or img.get("alt")}')

    def set_section(self, x):
        try:
            text = self._index[x]
            # name = self._sections[x]['line']
        except (TypeError, AttributeError, KeyError, IndexError):
            return
        self._gui_text.setText(f'{text}')
        self.set_image(self.get_image(x))

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
