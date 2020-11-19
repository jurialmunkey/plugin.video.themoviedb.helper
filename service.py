import xbmc
# from resources.lib.monitor.service import ServiceMonitor


if __name__ == '__main__':
    xbmc.Monitor().waitForAbort(5)  # Give things a momements breather to get started
    xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,restart_service)')  # Potential datetime fix for import lock by shelling to script first rather than running thread directly
    # ServiceMonitor().run()
