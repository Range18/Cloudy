import sys
import threading

from src.app.app_service import AppService
from src.app.cloud_service import CloudService
from src.app.file_handler import FileHandler
from src.configs.config_service import ConfigService
from src.core.exceptions.http_exception import HttpException
from src.core.types.app_mode_enum import AppMode


def main():
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        AppService.show_help()

    ConfigService.init_configs()
    config = ConfigService.get_config()

    path = AppService.choose_directory(config.path)
    service = AppService.choose_service(config)

    cloud_service = CloudService(service)
    cloud_service.authenticate()
    cloud_service.init_root(path.split("\\")[-1])

    event_handler = FileHandler(path, config.mode, cloud_service)

    observer_thread = threading.Thread(
        target=AppService.start_file_observer, args=(path, event_handler), daemon=True
    )
    observer_thread.start()

    print("File observer is running in background. You can type commands here:")

    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ("exit", "quit"):
                print("Exiting program...")
                break
            elif user_input.startswith("ls "):
                path = user_input[3:].strip()
                cloud_service.get_dir_files_list(path)
            elif user_input.startswith("get "):
                path = user_input[4:].strip()
                cloud_service.download_file(path)
            elif not user_input:
                continue
            else:
                print(f"Unknown command: {user_input}")
        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting...")
            break
        except Exception as e:
            if config.mode == AppMode.DEV:
                import traceback
                traceback.print_exc()
            elif isinstance(e, HttpException):
                print(f"Error: {e}")
                print(">")
            else:
                print("Unexpected error occurred. Try again.")


if __name__ == '__main__':
    main()
