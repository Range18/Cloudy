from src.app.google.google_disk_api_service import GoogleDriveApiService
from src.app.yandex.yandex_disk_api_service import YandexDiskApiService
from src.core.types.cloud_services_enum import CloudServices


class CloudService:
    def __init__(self, service: CloudServices):
        self.service = service
        if service == CloudServices.YANDEX:
            self.yandex_api_service = YandexDiskApiService()
        if service == CloudServices.GOOGLE:
            self.google_api_service = GoogleDriveApiService()

    def authenticate(self):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.authenticate()
        if self.service == CloudServices.GOOGLE:
            self.google_api_service.authenticate()

    def init_root(self, root):
        if self.service == CloudServices.YANDEX:
            is_file_exists = self.yandex_api_service.is_file_exists(root)
            if is_file_exists:
                return
            else:
                self.yandex_api_service.make_dir(root)
        if self.service == CloudServices.GOOGLE:
            pass

    def download_file(self, path):
        pass

    def create_file(self, path, destination, overwrite=False):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.upload_file(path, destination, overwrite)
        if self.service == CloudServices.GOOGLE:
            self.google_api_service.upload_file(path, destination, overwrite)

    def make_dir(self, path):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.make_dir(path)
        if self.service == CloudServices.GOOGLE:
            pass

    def remove_file_or_dir(self, path):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.remove_file_or_dir(path)
        if self.service == CloudServices.GOOGLE:
            pass

    def update(self, path, destination):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.update_file(path, destination)
        if self.service == CloudServices.GOOGLE:
            pass

    def move(self, from_path, to_path):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.move(from_path, to_path)
        if self.service == CloudServices.GOOGLE:
            pass

    def get_dir_files_list(self, path):
        if self.service == CloudServices.YANDEX:
            response = self.yandex_api_service.get_dir_files_list(path)

            for item in response["_embedded"]["items"]:
                print(item["name"])
        if self.service == CloudServices.GOOGLE:
            pass
