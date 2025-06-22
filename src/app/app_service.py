import os
import time

from watchdog.observers import Observer

from src.configs.config_service import ConfigService
from src.core.types.cloud_services_enum import CloudServices


class AppService:
    @staticmethod
    def show_help():
        print("Usage: python main.py [OPTIONS]")
        print("Options:")
        print("  -h, --help")
        exit(0)

    @staticmethod
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

    @staticmethod
    def choose_directory(path=None):
        if path and os.path.isdir(path):
            print(f"Using directory from configuration: {path}")
            return path

        manual_path = input("Enter directory path: ").strip()

        if manual_path:
            if os.path.isdir(manual_path):
                ConfigService.change_root(manual_path)
                return manual_path
            else:
                print("Invalid path. Exiting.")
                exit(1)

    @staticmethod
    def choose_service(config):
        service = None
        if len(config.services) == 0:
            choice = input("Choose a service:\n 1. Yandex Disk \n 2. Google Drive\n> ").strip()
            if choice == "1":
                service = CloudServices.YANDEX
            elif choice == "2":
                service = CloudServices.GOOGLE
            else:
                print("Unknown option. Exiting...")
                exit(1)
            ConfigService.add_service(service)
        else:
            service = CloudServices[config.services[0]]
        return service
