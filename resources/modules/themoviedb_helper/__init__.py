import sys
from xbmcaddon import Addon

addon_path = Addon('plugin.video.themoviedb.helper').getAddonInfo('path')
sys.path.append(addon_path)

from resources.lib.player.players import Players
from resources.lib.api.tmdb.api import TMDb
from resources.lib.player.details import get_next_episodes

__all__ = (
    'Players',
    'TMDb',
    'get_next_episodes',
)