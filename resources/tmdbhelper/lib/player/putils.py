def make_playlist(episode_queue):
    """ Make a playlist from a queue of episode items """
    from xbmc import PlayList, PLAYLIST_VIDEO
    playlist = PlayList(PLAYLIST_VIDEO)
    if playlist.getposition() != 0:  # If position isn't 0 then the user is already playing from the queue
        return  # We don't want to clear the existing queue so let's exit early
    playlist.clear()  # If there's an existing playlist but we're at position 0 then it might be old so clear it
    for listitem in episode_queue:  # Add all our episodes in the queue
        playlist.add(listitem.getPath(), listitem)


def make_upnext(current_episode, next_episode):
    import AddonSignals
    from tmdbhelper.lib.addon.consts import UPNEXT_EPISODE
    next_info = {
        'current_episode': {k: v(current_episode) for k, v in UPNEXT_EPISODE.items()},
        'next_episode': {k: v(next_episode) for k, v in UPNEXT_EPISODE.items()},
        'play_url': next_episode.url}
    AddonSignals.sendSignal('upnext_data', next_info, source_id='plugin.video.themoviedb.helper')
