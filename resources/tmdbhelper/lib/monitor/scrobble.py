from collections import namedtuple


ScrobbleResult = namedtuple('ScrobbleResult', 'successful history_changed')


class ScrobbleRequest:
    def __init__(self, player, provider):
        self.player = player
        self.provider = provider

    def scrobble(self, method):
        payload = self.get_scrobbler_item()
        if not payload:
            return ScrobbleResult(False, False)
        response = self.send_request(method, payload)
        if response is None:
            return ScrobbleResult(False, False)
        return self.get_result(method, response)

    def get_result(self, method, response):
        successful = response.status_code in (200, 201, 204)
        return ScrobbleResult(successful, successful and method == 'stop' and self.player.progress >= 80)

    def get_scrobbler_item(self):
        raise NotImplementedError

    def send_request(self, method, payload):
        raise NotImplementedError
