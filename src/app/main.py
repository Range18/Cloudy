import sys
import time
import threading

from watchdog.observers import Observer

from file_handler import FileHandler
from src.app.cloud_service import CloudService
from src.configs.config_service import ConfigService
from src.core.types.cloud_services_enum import CloudServices


def start_file_observer(path, event_handler):
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


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

    observer_thread = threading.Thread(
        target=start_file_observer, args=(config.path, event_handler), daemon=True
    )
    observer_thread.start()

    # Теперь ты можешь писать в консоль
    print("File observer is running in background. You can type commands here:")

    try:
        while True:
            user_input = input("> ")
            if user_input.lower() in ("exit", "quit"):
                print("Exiting program...")
                break
            if user_input.lower().split(" ")[0] == "ls":
                path = user_input.split(" ")[1]
                cloud_service.get_dir_files_list(path)
            else:
                print(f"You entered: {user_input}")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")


if __name__ == '__main__':
    main()
