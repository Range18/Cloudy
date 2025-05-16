import sys
import time

from watchdog.observers import Observer

from file_handler import FileHandler


def main():
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        print("Usage: python main.py [OPTIONS]")
        print("Options:")
        print("  -h, --help")
        exit(0)

    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, 'D:\PyProjects\Cloud\\test', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
