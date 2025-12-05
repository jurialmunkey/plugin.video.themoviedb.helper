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
    def ratings_queued(self):
        return self.listitem_monitor_functions.ratings_queued

    @property
    def ratings_thread(self):
        return self.listitem_monitor_functions.ratings_thread

    @ratings_thread.setter
    def ratings_thread(self, value):
        self.listitem_monitor_functions.ratings_thread = value

    @property
    def update_monitor(self):
        return self.service_monitor.update_monitor

    @property
    def mutex_lock(self):
        return self.service_monitor.mutex_lock

    @property
    def images_monitor(self):
        return self.service_monitor.images_monitor

    def ratings(self):
        if not self.item.is_same_item:  # Dont bother getting ratings if item changed before thread reached queued lookup
            return
        ratings = self.item.all_ratings
        if not self.item.is_same_item:  # Dont bother setting ratings if item changed before ratrings were retrieved
            return
        self.set_ratings(ratings)

    def artwork(self):
        self.images_monitor.remote_artwork[self.item.identifier] = self.item.artwork.copy()
        self.processed_artwork = self.images_monitor.update_artwork(forced=True) or {}

    def start_process_artwork(self):
        if not self.artwork_enabled:
            return
        if not self.item.artwork:
            return
        self.process_artwork()

    def process_artwork(self):
        self.get_property('IsUpdatingArtwork', 'True')
        with self.mutex_lock:  # Lock to avoid race with artwork monitor
            self.artwork()
        self.get_property('IsUpdatingArtwork', clear_property=True)

    def start_process_ratings(self):
        if not self.ratings_enabled:
            return

        if len(self.ratings_queued) < 1:
            self.ratings_queued.append(self.ratings)
        else:
            self.ratings_queued[0] = self.ratings

        if self.ratings_thread:
            return

        self.ratings_thread = SafeThread(target=self.process_ratings)
        self.ratings_thread.start()

    def process_ratings(self):
        self.get_property('IsUpdatingRatings', 'True')
        while self.ratings_thread and not self.update_monitor.abortRequested():
            try:
                func = self.ratings_queued.pop(0)
                func()
            except IndexError:
                break
        self.ratings_thread = None
        self.get_property('IsUpdatingRatings', clear_property=True)

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

        # Set some basic details next
        self.start_process_default()

        # Set ratings
        self.start_process_ratings()


class ListItemMonitorFinaliserContainerMethod(ListItemMonitorFinaliser):

    def start_process_default(self):
        with self.mutex_lock:
            self.listitem.setArt(self.processed_artwork)
            self.add_item_listcontainer(self.listitem)  # Add item to container

    def set_ratings(self, ratings):
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

    def set_ratings(self, ratings):
        self.set_ratings_properties({'ratings': ratings})

    def initial_checks(self):
        if not self.item:
            return False
        if not self.item.is_same_item:  # Check that we are still on the same item after building
            return False
        return True
