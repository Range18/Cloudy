import sys
import time

from watchdog.observers import Observer

from file_handler import FileHandler
from src.configs.config_service import ConfigService


def main():
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        print("Usage: python main.py [OPTIONS]")
        print("Options:")
        print("  -h, --help")
        exit(0)

    config_service = ConfigService()
    config_service.init_config()
    config = config_service.get_config()

    event_handler = FileHandler()
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
