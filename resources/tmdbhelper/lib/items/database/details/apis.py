from threading import Lock, local
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.api.contains import CommonContainerAPIs
from tmdbhelper.lib.api.tmdb.api import TMDb


class DetailsTMDb(TMDb):
    @property
    def api_url(self):
        if get_setting('use_alternate_api_url'):
            return 'https://api.tmdb.org/3'
        return 'https://api.themoviedb.org/3'


class DetailsAPIs:
    """Reuse provider sessions within a worker, without sharing mutable sessions."""

    def __init__(self):
        self.local = local()
        self.lock = Lock()
        self.contexts = set()

    def get(self, language):
        try:
            old_language, apis = self.local.context
        except AttributeError:
            pass
        else:
            if old_language == language:
                return apis
            self.close_context(apis)
            with self.lock:
                self.contexts.remove(apis)
        apis = CommonContainerAPIs()
        apis.tmdb_api = DetailsTMDb(language=language)
        self.local.context = (language, apis)
        with self.lock:
            self.contexts.add(apis)
        return apis

    @staticmethod
    def close_context(apis):
        for api in tuple(apis.__dict__.values()):
            session = getattr(api, '__dict__', {}).get('_session')
            if session is not None:
                session.close()

    def close(self):
        for apis in self.contexts:
            self.close_context(apis)
        self.contexts.clear()
