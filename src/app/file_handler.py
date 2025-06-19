from watchdog.events import FileSystemEventHandler
from os import path
from src.app.cloud_service import CloudService
from src.core.utils.encode_path import encode_relative_path


class FileHandler(FileSystemEventHandler):
    def __init__(self, root, cloud_service: CloudService):
        self.root = root
        self.root_parent = path.dirname(self.root)
        self.cloud_service = cloud_service

    def on_modified(self, event):
        print(f'Изменено: {event.src_path}')
        print(event.is_directory)
        if event.is_directory or "~" in event.src_path:
            return
        return self.cloud_service.update(event.src_path, encode_relative_path(event.src_path, self.root_parent))

    def on_created(self, event):
        print(f'Создано: {event.src_path}')
        if "~" in event.src_path:
            return
        encoded_path = encode_relative_path(event.src_path, self.root_parent)

        if event.is_directory:
            return self.cloud_service.make_dir(encoded_path)
        return self.cloud_service.create_file(event.src_path, encoded_path)

    def on_deleted(self, event):
        print(f'Удалено: {event.src_path}')
        if "~" in event.src_path:
            return
        return self.cloud_service.remove_file_or_dir(encode_relative_path(event.src_path, self.root_parent))

    def on_moved(self, event):
        print(f'Перемещено: из {event.src_path} в {event.dest_path}')
        if "~" in event.src_path:
            return
        self.cloud_service.move(encode_relative_path(event.src_path, self.root_parent),
                                encode_relative_path(event.dest_path, self.root_parent))
