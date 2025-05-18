import base64
import webbrowser
from urllib.parse import urljoin

import requests

from src.core.exceptions.http_exception import HttpException


class YandexDiskApiService:
    def __init__(self):
        self.host = "https://cloud-api.yandex.net"
        self.api_version = "v1"
        self.base_url = urljoin(self.host, self.api_version)
        self.client_id = "2a5ac65c1d3f4fefbfa3c218ea0a78de"
        self.base_headers = {"Authorization": "OAuth "}

    def authenticate(self, code=None):
        if code is None:
            webbrowser.open_new(f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self.client_id}")
            return
        try:
            print("TESST")
            print(base64.b64encode(":".encode()))
            headers = {"Authorization": f"Basic {
            base64.b64encode(":".encode())
            }", "Content-type": "application/x-www-form-urlencoded"}
            response = requests.post(f"https://oauth.yandex.ru",
                                     headers=headers, data={"grant_type": "authorization_code", "code": code})
            print(response.headers)
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return
        except HttpException as e:
            print("Error getting disk info")
            print(e)

    def get_disk_info(self):
        try:
            response = requests.get(self.base_url + "/disk", headers=self.base_headers)
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error getting disk info")
            print(e)

    def __get_download_link(self, path):
        try:
            response = requests.get(self.base_url + "/disk/resources/download",
                                    params={"path": path},
                                    headers=self.base_headers)
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
                                    headers=self.base_headers)
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
            if not response.ok:
                raise HttpException(response.text, response.status_code)
        except HttpException as e:
            print("Error uploading file")
            print(e)

    def make_dir(self, path):
        try:
            response = requests.put(self.base_url + "/disk/resources", params={"path": path}, headers=self.base_headers)
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
                                       headers=self.base_headers)
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error uploading file")
            print(e)

    # TODO implement
    def update_file(self):
        pass
