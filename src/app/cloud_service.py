from src.app.yandex.yandex_disk_api_service import YandexDiskApiService
from src.core.types.cloud_services_enum import CloudServices


class CloudService:
    def __init__(self):
        self.yandex_api_service = YandexDiskApiService()

    def authenticate(self, service: CloudServices):
        if service == CloudServices.YANDEX:
            self.yandex_api_service.authenticate()
        if service == CloudServices.GOOGLE:
            # TODO: implement google service
            pass

    def init_root(self, root, service: CloudServices):
        if service == CloudServices.YANDEX:
            is_file_exists = self.yandex_api_service.is_file_exists(root)
            if is_file_exists:
                return
            else:
                self.yandex_api_service.make_dir(root)

    def download_file(self, path):
        pass

    def create_file(self, path, destination, overwrite=False):
        self.yandex_api_service.upload_file(path, destination, overwrite)

    def make_dir(self, path):
        self.yandex_api_service.make_dir(path)

    def remove_file_or_dir(self, path):
        self.yandex_api_service.remove_file_or_dir(path)

    def update(self, path, destination):
        self.yandex_api_service.update_file(path, destination)

    def move(self, from_path, to_path):
        self.yandex_api_service.move(from_path, to_path)

    def get_dir_files_list(self, path):
        response = self.yandex_api_service.get_dir_files_list(path)

        for item in response["_embedded"]["items"]:
            print(item["name"])
