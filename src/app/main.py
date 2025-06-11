import sys
import time

from watchdog.observers import Observer

from file_handler import FileHandler
from src.app.cloud_service import CloudService
from src.configs.config_service import ConfigService
from src.core.types.cloud_services_enum import CloudServices


def main():
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        print("Usage: python main.py [OPTIONS]")
        print("Options:")
        print("  -h, --help")
        exit(0)

    config_service = ConfigService()
    config_service.init_configs()
    config = config_service.get_config()

    cloud_service = CloudService()
    cloud_service.authenticate(service=CloudServices.YANDEX)
    cloud_service.init_root(config.path.split("\\")[-1], CloudServices.YANDEX)

    event_handler = FileHandler(config.path)
    observer = Observer()
    observer.schedule(event_handler, config.path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
