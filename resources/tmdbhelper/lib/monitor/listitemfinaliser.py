from tmdbhelper.lib.addon.plugin import get_condvisibility
from tmdbhelper.lib.addon.thread import SafeThread
from jurialmunkey.ftools import cached_property


class ListItemMonitorFinaliser:
    def __init__(self, listitem_monitor_functions):
        self.listitem_monitor_functions = listitem_monitor_functions  # ListItemMonitorFunctions

    @cached_property
    def ratings_enabled(self):
        return get_condvisibility("!Skin.HasSetting(TMDbHelper.DisableRatings)")

    @cached_property
    def artwork_enabled(self):
        return get_condvisibility("!Skin.HasSetting(TMDbHelper.DisableArtwork)")

    @cached_property
    def processed_artwork(self):
        return {}

    @property
    def baseitem_properties(self):
        return self.listitem_monitor_functions.baseitem_properties

    @property
    def get_property(self):
        return self.listitem_monitor_functions.get_property

    @property
    def set_property(self):
        return self.listitem_monitor_functions.set_property

    @property
    def set_properties(self):
        return self.listitem_monitor_functions.set_properties

    @property
    def set_ratings_properties(self):
        return self.listitem_monitor_functions.set_ratings_properties

    @property
    def add_item_listcontainer(self):
        return self.listitem_monitor_functions.add_item_listcontainer

    @property
    def service_monitor(self):
        return self.listitem_monitor_functions.service_monitor

    @property
    def mutex_lock(self):
        return self.service_monitor.mutex_lock

    @property
    def images_monitor(self):
        return self.service_monitor.images_monitor

    def ratings(self):
        if not self.item.is_same_item:
            return
        self.set_ratings()

    def artwork(self):
        self.images_monitor.remote_artwork[self.item.identifier] = self.item.artwork.copy()
        self.processed_artwork = self.images_monitor.update_artwork(forced=True) or {}

    def process_artwork(self):
        self.get_property('IsUpdatingArtwork', 'True')
        self.artwork()
        self.get_property('IsUpdatingArtwork', clear_property=True)

    def process_ratings(self):
        self.get_property('IsUpdatingRatings', 'True')
        self.ratings()
        self.get_property('IsUpdatingRatings', clear_property=True)

    def start_process_artwork(self):
        if not self.artwork_enabled:
            return
        if not self.item.artwork:
            return
        with self.mutex_lock:  # Lock to avoid race with artwork monitor
            self.process_artwork()

    def start_process_ratings(self):
        if not self.ratings_enabled:
            return
        self.process_thread.append(SafeThread(target=self.process_ratings))
        if self.process_mutex:  # Already have one thread running a loop to clear out the queue
            return
        self.aquire_process_thread()

    def aquire_process_thread(self):
        self.process_mutex = True
        try:
            process_thread = self.process_thread.pop(0)
        except IndexError:
            self.process_mutex = False
            return
        process_thread.start()
        process_thread.join()
        return self.aquire_process_thread()

    @property
    def process_thread(self):
        return self.listitem_monitor_functions.process_thread

    @property
    def process_mutex(self):
        return self.listitem_monitor_functions.process_mutex

    @process_mutex.setter
    def process_mutex(self, value):
        self.listitem_monitor_functions.process_mutex = value

    @cached_property
    def item(self):
        return self.get_item()

    def get_item(self):
        item = self.listitem_monitor_functions._item
        self.set_property('monitor.tmdb_id', item.tmdb_id)
        self.set_property('monitor.tmdb_type', item.tmdb_type)
        self.set_property('monitor.season', item.season)
        self.set_property('monitor.episode', item.episode)
        return item

    @cached_property
    def listitem(self):
        listitem = self.listitem_monitor_functions._last_listitem = self.item.listitem
        return listitem

    def finalise(self):
        # Initial checks for item
        if not self.initial_checks():
            return

        # Set artwork to monitor as priority
        self.start_process_artwork()

        # Process ratings in thread to avoid holding up main loop
        t = SafeThread(target=self.start_process_ratings)
        t.start()

        # Set some basic details next
        self.start_process_default()


class ListItemMonitorFinaliserContainerMethod(ListItemMonitorFinaliser):

    def start_process_default(self):
        with self.mutex_lock:
            self.listitem.setArt(self.processed_artwork)
            self.add_item_listcontainer(self.listitem)  # Add item to container

    def set_ratings(self):
        ratings = self.item.all_ratings
        with self.mutex_lock:
            self.listitem.setProperties(ratings)

    def initial_checks(self):
        if not self.item:
            return False
        if not self.listitem:
            return False
        if not self.item.is_same_item:  # Check that we are still on the same item after building
            return False
        return True

    def get_item(self):
        item = super().get_item()
        item.set_additional_properties(self.baseitem_properties)
        return item


class ListItemMonitorFinaliserWindowMethod(ListItemMonitorFinaliser):

    def start_process_default(self):
        self.set_properties(self.item.item)

    def set_ratings(self):
        self.set_ratings_properties({'ratings': self.item.all_ratings})

    def initial_checks(self):
        if not self.item:
            return False
        if not self.item.is_same_item:
            return False
        return True
