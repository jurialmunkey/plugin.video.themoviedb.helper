from tmdbhelper.lib.api.contains import CommonContainerAPIs


class TraktAuthorisation(CommonContainerAPIs):
    authorisation_type = 'Trakt'

    @property
    def is_authorized(self):
        return self.trakt_api.authenticator.is_authorized
