from json import loads
from tmdbhelper.lib.addon.plugin import get_setting, get_localized
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.api.request import RequestAPI
from jurialmunkey.ftools import cached_property
import re


GEMINI_DEFAULT_MODEL_ID = "gemini-2.5-flash-lite"  # "gemini-2.5-flash-lite", "gemini-2.5-flash"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

QUERY_PROMPT_TEMPLATE_JSON_SHAPE = '''
{
  "recommendations": [
    {
      "title": "Name or Title 1",
      "year": 2000,
      "type": "Movie" | "Show",
      "reason": "Description for why this item is recommended"
    }
  ]
}
'''

QUERY_PROMPT_TEMPLATE_FIELD_RULES = '''
- Each recommendation MUST have a "type":
  - "Movie"  => a film / movie
  - "Show"   => a TV series / TV mini-series

- "year" SHOULD be a single 4-digit integer year when known.

- "reason" SHOULD be a sentence describing why you have made this recommendation

'''


QUERY_PROMPT_TEMPLATE = '''
You are a movie/TV recommendations engine.

You always respond with ONE JSON object, nothing else.

JSON OUTPUT SHAPE (MUST follow exactly):

{json_shape}

Field rules:

{field_rules}

LIMITS:

- You MUST NOT return more than 10 items.
- For general recommendation prompts ("recommend some...", "movies similar to..."),
  try to return 10 items, but fewer is allowed if appropriate.

PROMPT (the original user text to answer):

{prompt_text}

Now:

1. Produce ONE JSON object exactly in the shape above.
2. Do NOT include any explanation, comments, or extra text outside the JSON object.
'''


class Gemini(RequestAPI):

    api_key = get_setting('gemini_apikey', 'str')

    def __init__(self, api_key=None):
        api_key = api_key or self.api_key

        super(Gemini, self).__init__(
            req_api_name='Gemini',
            req_api_url=f"{GEMINI_API_BASE}/models/{GEMINI_DEFAULT_MODEL_ID}:generateContent",
            timeout=30,
        )

        Gemini.api_key = api_key

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

    @headers.setter
    def headers(self, value):
        """ Ignore base class req_api attempting to set headers """
        return

    def get_prompt_postdata(self, prompt_text):
        return {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt_text}]
                }
            ]
        }

    def get_prompt_query(self, prompt_text):
        return QUERY_PROMPT_TEMPLATE.format(
            json_shape=QUERY_PROMPT_TEMPLATE_JSON_SHAPE,
            field_rules=QUERY_PROMPT_TEMPLATE_FIELD_RULES,
            prompt_text=prompt_text
        )

    def get_prompt_request(self, prompt_text):
        return self.get_api_request_json(
            self.req_api_url,
            postdata=self.get_prompt_postdata(prompt_text),
            headers=self.headers,
            method='json'
        )

    def get_prompt_recommendations(self, prompt_text):
        data = self.get_prompt_text(self.get_prompt_query(prompt_text))
        if not data:
            return
        data = self.get_json_from_candidate(data)
        return data

    def get_prompt_items(self, prompt_text):
        data = self.get_prompt_recommendations(prompt_text)
        if not data:
            return
        data = self.get_tmdb_items(data)
        return data

    def get_prompt_text(self, prompt_text):
        data = self.get_prompt_request(prompt_text)
        if not data:
            return
        return self.get_candidates(data)

    def get_prompt_text_parsed(self, prompt_text):
        data = self.get_prompt_text(prompt_text)
        if not data:
            return
        return self.parse_string(data)

    @staticmethod
    def parse_bold(string):
        return Gemini.parse_regex(string, r'\*\*(.+?)\*\*', '[B]{}[/B]')

    @staticmethod
    def parse_italics(string):
        return Gemini.parse_regex(string, r'\*(.+?)\*', '[I]{}[/I]')

    @staticmethod
    def parse_regex(string, regex, restr):
        match = re.search(regex, string)
        if not match:
            return string
        string = string.replace(match.group(0), restr.format(match.group(1)))
        return Gemini.parse_regex(string, regex, restr)

    @staticmethod
    def parse_string(string):
        string = string.replace('*  ', '•  ')
        string = Gemini.parse_bold(string)
        string = Gemini.parse_italics(string)
        string = string.replace('\n', '[CR]')
        return string

    @cached_property
    def database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    def get_tmdb_item(self, i):

        try:
            name = i['title']
            year = i['year']
            mode = i['type']
        except (TypeError, KeyError):
            kodi_log(f'Geimini INVALID SPEC: {i}', 1)
            return

        if mode not in ('Movie', 'Show'):
            kodi_log(f'Geimini INVALID SPEC: {i}', 1)
            return

        tmdb_type = 'movie' if mode == 'Movie' else 'tv'
        tmdb_id = self.database.get_tmdb_id(tmdb_type=tmdb_type, query=name, year=year)
        tmdb_id = tmdb_id or self.database.get_tmdb_id(tmdb_type=tmdb_type, query=name)  # Try again without year

        if not tmdb_id:
            kodi_log(f'Geimini UNKNOWN ITEM: {i}', 1)
            return

        reason = i.get('reason') or ''

        item = {
            'infolabels': {
                'mediatype': 'movie' if tmdb_type == 'movie' else 'tvshow',
            },
            'infoproperties': {
                'plot_affix': f'[B]Gemini {get_localized(32223)}:[/B] {reason}[CR]',
                'reason': reason,
            },
            'unique_ids': {
                'tmdb': tmdb_id,
            },
            'params': {
                'info': 'details',
                'tmdb_type': tmdb_type,
                'tmdb_id': tmdb_id,
            }
        }

        return item

    def get_tmdb_items(self, data):

        try:
            data = data['recommendations']
        except (TypeError, KeyError):
            kodi_log(f'Geimini FAILED: Unable to locate recommendations data', 1)
            return

        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread(data, self.get_tmdb_item) as pt:
            items = pt.queue

        return [i for i in items if i]

    @staticmethod
    def get_candidates(data):
        try:
            parts = data['candidates'][0]['content']['parts']
        except (TypeError, IndexError, KeyError):
            kodi_log(f'Geimini FAILED: Unable to get parts', 1)
            return
        if not parts:
            kodi_log(f'Geimini FAILED: Unable to get parts', 1)
            return
        return "".join(part.get("text", "") for part in parts).strip()

    @staticmethod
    def get_json_from_candidate(text):
        """
        Given raw text from the model, find the first {...} block and parse it as JSON.
        This lets us ignore any accidental extra text.
        """
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            kodi_log(f'Geimini FAILED: Unable to find json data', 1)
            return
        return loads(text[start:end + 1])
