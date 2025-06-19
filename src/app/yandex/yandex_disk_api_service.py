import base64
import json
import webbrowser
from urllib.parse import urljoin

import requests

from src.configs.config_service import ConfigService
from src.core.exceptions.http_exception import HttpException
from src.core.singleton import Singleton


class YandexDiskApiService(metaclass=Singleton):
    def __init__(self):
        self.token_file = "yandex_session.json"
        config = ConfigService().get_yandex_config()
        self.host = "https://cloud-api.yandex.net"
        self.api_version = "v1"
        self.base_url = urljoin(self.host, self.api_version)
        self._client_id = config.client_id
        self._client_secret = config.client_secret
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

    def _get_base_headers(self):
        return {"Authorization": f"OAuth {self.access_token}"}

    def authenticate(self):
        try:
            webbrowser.open_new(
                f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self._client_id}"
            )
            code = input("Введите код со страницы: ")

            encoded = base64.b64encode(
                f"{self._client_id}:{self._client_secret}".encode()
            )
            headers = {
                "Authorization": f"Basic {encoded.decode()}",
                "Content-type": "application/x-www-form-urlencoded"
            }

            data = {
                "grant_type": "authorization_code",
                "code": code
            }

            response = requests.post("https://oauth.yandex.ru/token", headers=headers, data=data)
            tokens = response.json()

            if not response.ok:
                raise HttpException(response.text, response.status_code)

            self.access_token = tokens.get("access_token")

            # Сохраняем токены в файл
            with open(self.token_file, "w", encoding="utf-8") as f:
                json.dump(tokens, f, ensure_ascii=False, indent=4)

            print("Вы успешно авторизовались. Токены сохранены в файл.")
        except HttpException as e:
            print("Ошибка авторизации с помощью Яндекс.Диск")
            print(e)
        except Exception as e:
            print("Произошла непредвиденная ошибка:")
            print(e)

    def get_dir_files_list(self, path):
        try:
            response = requests.get(self.base_url + "/disk/resources", params={"path": path}, headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error getting disk info")
            print(e)

    def get_disk_info(self):
        try:
            response = requests.get(self.base_url + "/disk", headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error getting disk info")
            print(e)

    def get_file_meta(self, path):
        try:
            response = requests.get(self.base_url + "/disk/resources", params={"path": path},
                                    headers=self._get_base_headers())
            if response.status_code == 404:
                return None
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error getting file meta info")
            print(e)

    def is_file_exists(self, path):
        return bool(self.get_file_meta(path))

    def __get_download_link(self, path):
        try:
            response = requests.get(self.base_url + "/disk/resources/download",
                                    params={"path": path},
                                    headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error getting download link")
            print(e)

    def download_file(self, path):
        # TODO: safe file
        try:
            download_link_json = self.__get_download_link(path)
            response = requests.get(download_link_json["href"])
            if not response.ok:
                raise HttpException(response.text, response.status_code)
        except HttpException as e:
            print("Error downloading file")
            print(e)

    def __get_upload_link(self, path, overwrite=False):
        try:
            response = requests.get(self.base_url + "/disk/resources/upload",
                                    params={"path": path, "overwrite": overwrite},
                                    headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error getting upload link")
            print(e)

    def upload_file(self, path, destination, overwrite=False):
        try:
            upload_link_json = self.__get_upload_link(destination, overwrite)
            response = requests.put(upload_link_json["href"], data=open(path, "rb"))
            print(response)
            if not response.ok:
                raise HttpException(response.text, response.status_code)
        except HttpException as e:
            print("Error uploading file")
            print(e)

    def make_dir(self, path):
        try:
            response = requests.put(self.base_url + "/disk/resources", params={"path": path},
                                    headers=self._get_base_headers())
            print(response)
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error uploading file")
            print(e)

    def remove_file_or_dir(self, path):
        try:
            response = requests.delete(self.base_url + "/disk/resources",
                                       params={"path": path, "permanently": "true", "force_async": "true"},
                                       headers=self._get_base_headers())
            print(response)
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error deleting file or directory")
            print(e)

    def update_file(self, path, destination):
        self.upload_file(path, destination, overwrite=True)

    def move(self, from_rel_path, to_rel_path, overwrite=False):
        try:
            response = requests.post(self.base_url + "/disk/resources/move",
                                     params={"from": from_rel_path, "path": to_rel_path, "overwrite": overwrite,
                                             "force_async": "true"},
                                     headers=self._get_base_headers())
            print(response)
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error moving file pr directory")
            print(e)
