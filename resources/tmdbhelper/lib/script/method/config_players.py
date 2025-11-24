def set_defaultplayer(set_defaultplayer, **kwargs):
    from tmdbhelper.lib.player.config.default import PlayerDefault
    return PlayerDefault(set_defaultplayer).select()


def set_chosenplayer(set_chosenplayer, **kwargs):
    from tmdbhelper.lib.player.config.chosen import PlayerChosenSet
    return PlayerChosenSet(**kwargs).update()


def customise_players():
    from tmdbhelper.lib.player.config.customise.menu import PlayerCustomiseDialogMenu
    PlayerCustomiseDialogMenu()
