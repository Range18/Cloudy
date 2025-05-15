from watchdog.events import FileSystemEventHandler
from os import path
from src.app.cloud_service import CloudService


class FileHandler(FileSystemEventHandler):
    def __init__(self):
        self.root = 'D:\PyProjects\Cloud\\test'
        self.cloud_service = CloudService()

    def on_modified(self, event):
        print(f'Изменено: {event.src_path}')

    def on_created(self, event):
        print(f'Создано: {event.src_path}')
        if event.is_directory:
            return self.cloud_service.make_dir(path.relpath(event.src_path, self.root))
        return self.cloud_service.create_file(event.src_path, path.relpath(event.src_path, self.root))

    def on_deleted(self, event):
        print(f'Удалено: {event.src_path}')
        return self.cloud_service.remove_file_or_dir(path.relpath(event.src_path, self.root))

    def on_moved(self, event):
        print(f'Перемещено: из {event.src_path} в {event.dest_path}')
