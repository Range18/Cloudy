from urllib.parse import urljoin

import requests

from src.core.exceptions.http_exception import HttpException


class YandexDiskApiService:
    def __init__(self):
        self.host = "https://cloud-api.yandex.net"
        self.api_version = "v1"
        self.base_url = urljoin(self.host, self.api_version)
        self.access_token = ""
        self.base_headers = {"Authorization": "OAuth " + self.access_token}

    def authenticate(self):
        pass

    def get_disk_info(self):
        try:
            response = requests.get(self.base_url + "/disk", headers=self.base_headers)
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Error getting disk info")
            print(e)

    def download_file(self):
        pass

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
            print(upload_link_json)
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
