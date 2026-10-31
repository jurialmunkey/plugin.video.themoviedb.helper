from tmdbhelper.lib.monitor.service import ServiceMonitor
from tmdbhelper.lib.items.database.details.client import DetailsClient


if __name__ == '__main__':
    DetailsClient().start()
    ServiceMonitor().run()
