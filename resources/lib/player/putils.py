from resources.lib.addon.consts import PLAYERS_BASEDIR_BUNDLED, PLAYERS_BASEDIR_USER, PLAYERS_BASEDIR_SAVE
from resources.lib.addon.plugin import get_setting, get_condvisibility
from resources.lib.files.futils import get_files_in_folder, read_file
from json import loads


def get_players_from_file():
    players = {}
    basedirs = [PLAYERS_BASEDIR_USER]
    if get_setting('bundled_players'):
        basedirs += [PLAYERS_BASEDIR_BUNDLED]
    basedirs += [PLAYERS_BASEDIR_SAVE]  # Add saved players last so they overwrite
    for basedir in basedirs:
        files = get_files_in_folder(basedir, r'.*\.json')
        for file in files:
            meta = loads(read_file(basedir + file)) or {}
            plugins = meta.get('plugin') or 'plugin.undefined'  # Give dummy name to undefined plugins so that they fail the check
            plugins = plugins if isinstance(plugins, list) else [plugins]  # Listify for simplicity of code
            for i in plugins:
                if not get_condvisibility(f'System.AddonIsEnabled({i})'):
                    break  # System doesn't have a required plugin so skip this player
            else:
                meta['plugin'] = plugins[0]
                players[file] = meta
    return players
