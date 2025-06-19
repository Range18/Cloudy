import sys
import threading

from file_handler import FileHandler
from src.app.app_service import AppService
from src.app.cloud_service import CloudService
from src.configs.config_service import ConfigService
from src.core.types.cloud_services_enum import CloudServices


def main():
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        AppService.show_help()

    config_service = ConfigService()
    config_service.init_configs()
    config = config_service.get_config()

    service = AppService.choose_service(config, config_service)

    cloud_service = CloudService(service)
    cloud_service.authenticate()
    cloud_service.init_root(config.path.split("\\")[-1])

    event_handler = FileHandler(config.path, cloud_service)

    observer_thread = threading.Thread(
        target=AppService.start_file_observer, args=(config.path, event_handler), daemon=True
    )
    observer_thread.start()

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
