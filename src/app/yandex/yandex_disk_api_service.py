import base64
import json
import os
import time
import webbrowser
from urllib.parse import urljoin

import requests

from src.configs.config_service import ConfigService
from src.core.exceptions.http_exception import HttpException
from src.core.singleton import Singleton


class YandexDiskApiService(metaclass=Singleton):
    def __init__(self):
        self.token_file = "yandex_session.json"
        config = ConfigService.get_yandex_config()
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

    def _save_session(self, tokens):
        self.access_token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")  # Not always provided
        expires_in = tokens.get("expires_in", 3600)
        self.token_expires_at = int(time.time()) + expires_in

        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump({
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "token_expires_at": self.token_expires_at
            }, f, ensure_ascii=False, indent=2)

    def _load_session(self):
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    self.token_expires_at = data.get("token_expires_at")
            except (json.JSONDecodeError, IOError) as e:
                print("Error loading tokens from file:", e)

    def _is_token_valid(self):
        return self.access_token and self.token_expires_at and int(time.time()) < self.token_expires_at - 60

    def authenticate(self):
        self._load_session()
        if self._is_token_valid():
            print("Using saved access_token.")
            return

        if self.refresh_token:
            try:
                self._refresh_token()
                print("access_token refreshed using refresh_token.")
                return
            except Exception as e:
                print("Error refreshing token. Proceeding with full authorization.", e)

        self._full_auth_flow()

    def _full_auth_flow(self):
        try:
            webbrowser.open_new(
                f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self._client_id}"
            )
            code = input("Enter the code from the browser: ").strip()

            auth_header = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "grant_type": "authorization_code",
                "code": code
            }

            response = requests.post("https://oauth.yandex.ru/token", headers=headers, data=data)
            if not response.ok:
                raise HttpException(response.text, response.status_code)

            tokens = response.json()
            self._save_session(tokens)
            print("Authentication completed successfully.")
        except Exception as e:
            print("Error obtaining token:", e)

    def _refresh_token(self):
        if not self.refresh_token:
            raise Exception("refresh_token is missing.")

        auth_header = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        response = requests.post("https://oauth.yandex.ru/token", headers=headers, data=data)
        if not response.ok:
            raise HttpException(response.text, response.status_code)

        tokens = response.json()
        self._save_session(tokens)

    def _ensure_authenticated(self):
        self.authenticate()

    def get_dir_files_list(self, path):
        try:
            response = requests.get(self.base_url + "/disk/resources",
                                    params={"path": f"{ConfigService.get_config().root}{path}"},
                                    headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Failed to retrieve directory file list.")
            print(e)

    def get_disk_info(self):
        try:
            response = requests.get(self.base_url + "/disk", headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Unable to fetch disk information.")
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
            print("Failed to get file metadata.")
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
            print("Failed to get download link.")
            print(e)

    def download_file(self, path, save_to=None):
        try:
            download_link_json = self.__get_download_link(path)
            download_url = download_link_json["href"]

            response = requests.get(download_url, stream=True)
            if not response.ok:
                raise HttpException(response.text, response.status_code)

            filename = save_to or os.path.basename(path)

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"File downloaded and saved as: {filename}")

        except HttpException as e:
            print("Error occurred while downloading the file.")
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
            print("Failed to retrieve upload link.")
            print(e)

    def upload_file(self, path, destination, overwrite=False):
        try:
            upload_link_json = self.__get_upload_link(destination, overwrite)
            response = requests.put(upload_link_json["href"], data=open(path, "rb"))
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            print(f"File '{path}' uploaded to '{destination}'.")
        except HttpException as e:
            print("File upload failed.")
            print(e)

    def make_dir(self, path):
        try:
            response = requests.put(self.base_url + "/disk/resources", params={"path": path},
                                    headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Failed to create directory.")
            print(e)

    def remove_file_or_dir(self, path):
        try:
            response = requests.delete(self.base_url + "/disk/resources",
                                       params={"path": path, "permanently": "true", "force_async": "true"},
                                       headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error deleting file or folder.")
            print(e)

    def update_file(self, path, destination):
        self.upload_file(path, destination, overwrite=True)

    def move(self, from_rel_path, to_rel_path, overwrite=False):
        try:
            response = requests.post(self.base_url + "/disk/resources/move",
                                     params={"from": from_rel_path, "path": to_rel_path, "overwrite": overwrite,
                                             "force_async": "true"},
                                     headers=self._get_base_headers())
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Failed to move file or directory.")
            print(e)
