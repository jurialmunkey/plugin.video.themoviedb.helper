from jurialmunkey.parser import try_type, try_int
from tmdbhelper.lib.addon.plugin import get_infolabel, executebuiltin, get_condvisibility
from tmdbhelper.lib.files.ftools import cached_property


class WindowProperty:

    prefix = 'TMDbHelper'
    conversion_type = str
    window_id = 'Home'

    def __init__(self, window_id=None, prefix=None):
        self.window_id = None if window_id == 'current' else window_id or self.window_id
        self.prefix = prefix or self.prefix

    @cached_property
    def xbmc_monitor(self):
        from xbmc import Monitor
        return Monitor()

    @property
    def property_name(self):
        if self.prefix == -1:
            return self.name
        return f'{self.prefix}.{self.name}'

    def add_propname(self, name):
        self.name = name

    @property
    def property_getpath(self):
        if not self.window_id:
            return f'Window.Property({self.property_name})'
        return f'Window({self.window_id}).Property({self.property_name})'

    @property
    def property_setpath(self):
        if not self.window_id:
            return f'SetProperty({self.property_name},{{}})'
        return f'SetProperty({self.property_name},{{}},{self.window_id})'

    @property
    def property_delpath(self):
        if not self.window_id:
            return f'ClearProperty({self.property_name})'
        return f'ClearProperty({self.property_name},{self.window_id})'

    @property
    def property_visible(self):
        return f'Window.IsVisible({self.window_id})'

    @property
    def property_close(self):
        return f'Dialog.Close({self.window_id})'

    @property
    def property_force_close(self):
        return f'Dialog.Close({self.window_id},true)'

    @property
    def property_activate(self):
        return f'ActivateWindow({self.window_id})'

    @property
    def is_visible(self):
        return get_condvisibility(self.property_visible)

    def is_inactive(self, invert=False):
        if self.is_visible:
            return True if invert else False
        return True if not invert else False

    def property_is_value(self, name, value):
        return (
            bool(self.get_property(name))
            if value else
            bool(not self.get_property(name))
        )

    @staticmethod
    def container_is_updating(container_id):
        return bool(
            get_condvisibility(f"Container({container_id}).IsUpdating")
            or not try_int(get_infolabel(f"Container({container_id}).NumItems"))
        )

    def wait_for_property(self, name, value=None, poll=1, timeout=10):
        """
        Waits until property matches value. None value waits for property to be cleared.
        Will set property to value if set_property flag is set. None value clears property.
        Returns True when successful.
        """

        while (
                not self.xbmc_monitor.abortRequested() and timeout > 0
                and not self.property_is_value(name, value)
        ):
            self.xbmc_monitor.waitForAbort(poll)
            timeout -= poll
        if timeout > 0:
            return True

    def wait_until_active(self, instance_id=None, poll=1, timeout=30, invert=False):
        """
        Wait for window ID to open (or to close if invert set to True). Returns window_id if successful.
        """
        while (
                not self.xbmc_monitor.abortRequested() and timeout > 0
                and self.is_inactive(invert)
                and (not instance_id or WindowProperty(instance_id).is_visible)
        ):
            self.xbmc_monitor.waitForAbort(poll)
            timeout -= poll
        if timeout > 0 and (not instance_id or WindowProperty(instance_id).is_visible):
            return self.window_id

    def wait_until_updated(self, container_id=9999, poll=1, timeout=60):
        """
        Wait for container to update. Returns container_id if successful
        Pass instance_id if there is also a base window that needs to be open underneath
        """
        while (
                not self.xbmc_monitor.abortRequested() and timeout > 0
                and self.container_is_updating(container_id)
                and self.is_visible
        ):
            self.xbmc_monitor.waitForAbort(poll)
            timeout -= poll
        if timeout > 0 and self.is_visible:
            return container_id

    def close(self, force=False):
        if not force:
            return executebuiltin(self.property_close)
        return executebuiltin(self.property_force_close)

    def activate(self):
        return executebuiltin(self.property_activate)

    def get_property(self, name):
        self.add_propname(name)
        self.value = try_type(get_infolabel(self.property_getpath), self.conversion_type)
        return self.value

    def set_property(self, name, value, clear_property=False):
        self.add_propname(name)
        self.del_property(name) if clear_property else None
        executebuiltin(self.property_setpath.format(value))
        return self.get_property(name)

    def del_property(self, name):
        self.add_propname(name)
        executebuiltin(self.property_delpath)
        return self.get_property(name)
