import xbmc


class ServiceMonitor(object):
    def __init__(self):
        self.monitor = xbmc.Monitor()
        self.monitor_listitem()

    def monitor_listitem(self):
        while not self.monitor.abortRequested():
            # skip when modal dialogs are opened (e.g. textviewer in musicinfo dialog)
            if xbmc.getCondVisibility(
                    "Window.IsActive(DialogSelect.xml) | Window.IsActive(progressdialog) | "
                    "Window.IsActive(contextmenu) | Window.IsActive(busydialog)"):
                self.kodimonitor.waitForAbort(2)

            # skip when container scrolling
            elif xbmc.getCondVisibility(
                    "Container.OnScrollNext | Container.OnScrollPrevious | Container.Scrolling"):
                self.kodimonitor.waitForAbort(1)

            # media window is opened or widgetcontainer set - start listitem monitoring!
            elif xbmc.getCondVisibility(
                    "Window.IsMedia | !IsEmpty(Window(Home).Property(SkinHelper.WidgetContainer))"):
                # DO SOMETHING HERE MONITOR LISTITEM
                self.kodimonitor.waitForAbort(0.15)


if __name__ == '__main__':
    ServiceMonitor()
