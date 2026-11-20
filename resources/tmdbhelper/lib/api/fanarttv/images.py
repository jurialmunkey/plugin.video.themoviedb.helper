from urllib.parse import quote
from jurialmunkey.ftools import cached_property


UNRESERVED_CHARACTERS = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')
SAFE_WITH_PERCENT = "!#$%&'()*+,/:;=?@[]~"
SAFE_WITHOUT_PERCENT = "!#$&'()*+,/:;=?@[]~"


class RequotedImagePath:
    """Requotes an image URL as requests.utils.requote_uri does, without importing requests."""

    def __init__(self, uri):
        self.uri = uri

    @cached_property
    def unquoted_unreserved(self):
        return self.get_unquoted_unreserved()

    def get_unquoted_unreserved(self):
        head, *escapes = self.uri.split('%')
        return ''.join((head, *(self.get_unquoted_escape(i) for i in escapes)))

    @staticmethod
    def get_unquoted_escape(part):
        code = part[:2]
        if len(code) != 2 or not code.isalnum():
            return f'%{part}'
        character = chr(int(code, 16))  # ValueError for an invalid escape such as %zz
        return f'{character}{part[2:]}' if character in UNRESERVED_CHARACTERS else f'%{part}'

    @cached_property
    def requoted(self):
        return self.get_requoted()

    def get_requoted(self):
        try:
            return quote(self.unquoted_unreserved, safe=SAFE_WITH_PERCENT)
        except ValueError:
            return quote(self.uri, safe=SAFE_WITHOUT_PERCENT)


def get_imagepath_requoted(v):
    return RequotedImagePath(v).requoted
