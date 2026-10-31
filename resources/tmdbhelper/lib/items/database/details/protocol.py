import json
import socket
import struct
from hashlib import sha256
from time import monotonic
from xbmcgui import Window
from xbmcvfs import translatePath


PROTOCOL_VERSION = 1
MAX_MESSAGE_BYTES = 32 * 1024 * 1024
MAX_REQUEST_ITEMS = 2000


class DetailsServiceError(RuntimeError):
    pass


class DetailsServiceUnavailable(DetailsServiceError):
    pass


class ServiceLocation:
    def __init__(self):
        profile = translatePath('special://profile/')
        self.name = f'TMDbHelper.Details.{sha256(profile.encode("utf-8")).hexdigest()}'

    @property
    def endpoint(self):
        value = Window(10000).getProperty(self.name)
        return json.loads(value) if value else None

    @endpoint.setter
    def endpoint(self, value):
        window = Window(10000)
        if value is None:
            window.clearProperty(self.name)
        else:
            window.setProperty(self.name, json.dumps(value))

    @property
    def restart(self):
        return Window(10000).getProperty(f'{self.name}.Restart')

    @restart.setter
    def restart(self, value):
        Window(10000).setProperty(f'{self.name}.Restart', value)


def receive_exact(connection, size, monitor, deadline):
    data = bytearray()
    while len(data) < size and not monitor.abortRequested():
        if monotonic() >= deadline:
            raise DetailsServiceUnavailable('Item detail service response timed out')
        try:
            part = connection.recv(size - len(data))
        except socket.timeout:
            continue
        if not part:
            raise DetailsServiceUnavailable('Item detail service connection closed')
        data.extend(part)
    if len(data) != size:
        raise DetailsServiceUnavailable('Kodi is shutting down')
    return data


def receive_message(connection, monitor, timeout=300):
    deadline = monotonic() + timeout
    size = struct.unpack('!I', receive_exact(connection, 4, monitor, deadline))[0]
    if size > MAX_MESSAGE_BYTES:
        raise DetailsServiceError('Item detail service message is too large')
    return json.loads(receive_exact(connection, size, monitor, deadline))


def send_message(connection, message):
    data = json.dumps(message, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    if len(data) > MAX_MESSAGE_BYTES:
        raise DetailsServiceError('Item detail service message is too large')
    connection.sendall(struct.pack('!I', len(data)) + data)
