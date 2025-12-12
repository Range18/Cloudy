from src.app.google.google_disk_api_service import GoogleDriveApiService
from src.app.yandex.yandex_disk_api_service import YandexDiskApiService
from src.configs.config_service import ConfigService
from src.core.types.cloud_services_enum import CloudServices
from src.core.utils.normalize_path import normalize_path


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
        elif self.service == CloudServices.GOOGLE:
            existing_folders = self.google_api_service.list_files(
                query=f"name='{root}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            )
            if existing_folders:
                return
            self.google_api_service.create_folder(root)

    def download_file(self, path, save_to):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.download_file(
                normalize_path(ConfigService.get_config().root + path), save_to
            )

    def create_file(self, path, destination, overwrite=False):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.upload_file(path, destination, overwrite)
        if self.service == CloudServices.GOOGLE:
            self.google_api_service.upload_file(path, destination)

    def make_dir(self, path):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.make_dir(path)
        if self.service == CloudServices.GOOGLE:
            self.google_api_service.create_folder(path)

    def remove_file_or_dir(self, path):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.remove_file_or_dir(path)
        if self.service == CloudServices.GOOGLE:
            file = self._get_file_by_name(path)
            if file:
                self.google_api_service.delete_file_or_folder(file["id"])

    def _get_file_by_name(self, name):
        files = self.google_api_service.list_files(f"name='{name}' and trashed=false")
        return files[0] if files else None

    def update(self, path, destination):
        if self.service == CloudServices.YANDEX:
            self.yandex_api_service.update_file(path, destination)
        if self.service == CloudServices.GOOGLE:
            self.google_api_service.update_file(path, destination)

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
