import json
import os
import time
import webbrowser
from urllib.parse import urlencode

import requests

from src.configs.config_service import ConfigService
from src.core.exceptions.http_exception import HttpException
from src.core.singleton import Singleton


class GoogleDriveApiService(metaclass=Singleton):
    def __init__(self):
        config = ConfigService().get_google_config().installed
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.redirect_uri = config.redirect_uris[0]
        self.api_base = "https://www.googleapis.com/drive/v3"
        self.upload_url = "https://www.googleapis.com/upload/drive/v3/files"
        self.session_path = "google_session.json"

        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

        self._load_session()

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def _save_session(self, tokens):
        self.token_expires_at = int(time.time()) + tokens.get("expires_in", 3600)
        with open(self.session_path, "w", encoding="utf-8") as f:
            json.dump({
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "token_expires_at": self.token_expires_at
            }, f, ensure_ascii=False, indent=2)

    def _load_session(self):
        if os.path.exists(self.session_path):
            with open(self.session_path, "r", encoding="utf-8") as f:
                session = json.load(f)
                self.access_token = session.get("access_token")
                self.refresh_token = session.get("refresh_token")
                self.token_expires_at = session.get("token_expires_at")

    def _refresh_access_token(self):
        if not self.refresh_token:
            print("Нет refresh_token. Необходимо авторизоваться.")
            self.authenticate()
            return

        print("Обновляем access_token...")
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }

        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        if not response.ok:
            raise HttpException(response.text, response.status_code)

        tokens = response.json()
        self.access_token = tokens.get("access_token")
        self._save_session(tokens)
        print("Токен успешно обновлён.")

    def authenticate(self):
        # Проверка сохранённых токенов
        now = int(time.time())
        if self.access_token and self.token_expires_at and now < self.token_expires_at - 60:
            print("Используется сохранённый access_token.")
            return
        elif self.refresh_token:
            try:
                self._refresh_access_token()
                return
            except HttpException:
                print("Ошибка обновления токена. Выполняется полная авторизация.")

        # Новая авторизация
        print("Запуск новой авторизации через Google...")
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?" +
            urlencode({
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "response_type": "code",
                "scope": "https://www.googleapis.com/auth/drive",
                "access_type": "offline",
                "prompt": "consent"
            })
        )
        webbrowser.open_new(auth_url)
        code = input("Введите код (code) из URL после авторизации: ")

        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }

        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        if not response.ok:
            raise HttpException(response.text, response.status_code)

        tokens = response.json()
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens.get("refresh_token")
        self._save_session(tokens)

        print("Вы успешно авторизовались.")

    def _ensure_authenticated(self):
        self.authenticate()

    def list_files(self, query="trashed=false"):
        self._ensure_authenticated()
        try:
            response = requests.get(
                f"{self.api_base}/files",
                headers=self._get_headers(),
                params={"q": query, "fields": "files(id, name, mimeType)"}
            )
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json().get("files", [])
        except HttpException as e:
            print("Ошибка получения списка файлов")
            print(e)

    def get_file_metadata(self, file_id):
        self._ensure_authenticated()
        try:
            response = requests.get(
                f"{self.api_base}/files/{file_id}",
                headers=self._get_headers(),
                params={"fields": "id, name, mimeType, parents"}
            )
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Ошибка получения метаданных файла")
            print(e)

    def download_file(self, file_id, destination_path):
        self._ensure_authenticated()
        try:
            response = requests.get(
                f"{self.api_base}/files/{file_id}?alt=media",
                headers=self._get_headers(),
                stream=True
            )
            if not response.ok:
                raise HttpException(response.text, response.status_code)

            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except HttpException as e:
            print("Ошибка скачивания файла")
            print(e)

    def upload_file(self, filepath, filename, parent_id=None):
        self._ensure_authenticated()
        try:
            metadata = {"name": filename}
            if parent_id:
                metadata["parents"] = [parent_id]

            files = {
                "metadata": ("metadata", json.dumps(metadata), "application/json"),
                "file": open(filepath, "rb")
            }

            response = requests.post(
                f"{self.upload_url}?uploadType=multipart",
                headers=self._get_headers(),
                files=files
            )
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Ошибка загрузки файла")
            print(e)

    def create_folder(self, name, parent_id=None):
        self._ensure_authenticated()
        try:
            metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder"
            }
            if parent_id:
                metadata["parents"] = [parent_id]

            response = requests.post(
                f"{self.api_base}/files",
                headers={**self._get_headers(), "Content-Type": "application/json"},
                json=metadata
            )
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Ошибка создания папки")
            print(e)

    def delete_file_or_folder(self, file_id):
        self._ensure_authenticated()
        try:
            response = requests.delete(
                f"{self.api_base}/files/{file_id}",
                headers=self._get_headers()
            )
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return True
        except HttpException as e:
            print("Ошибка удаления файла или папки")
            print(e)

    def move_file(self, file_id, new_parent_id):
        self._ensure_authenticated()
        try:
            file = self.get_file_metadata(file_id)
            old_parents = ",".join(file.get("parents", []))
            response = requests.patch(
                f"{self.api_base}/files/{file_id}",
                headers=self._get_headers(),
                params={"addParents": new_parent_id, "removeParents": old_parents, "fields": "id, parents"}
            )
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        except HttpException as e:
            print("Ошибка перемещения файла")
            print(e)

    def update_file(self, filepath, filename, parent_id=None):
        self._ensure_authenticated()

        # Проверка, существует ли файл с таким именем в папке
        query = f"name='{filename}' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        files = self.list_files(query=query)
        if files:
            file_id = files[0]['id']
            print(f"Файл {filename} найден, обновляется...")
            metadata = {"name": filename}
            if parent_id:
                metadata["parents"] = [parent_id]

            files = {
                "metadata": ("metadata", json.dumps(metadata), "application/json"),
                "file": open(filepath, "rb")
            }

            response = requests.patch(
                f"{self.upload_url}/{file_id}?uploadType=multipart",
                headers=self._get_headers(),
                files=files
            )
            if not response.ok:
                raise HttpException(response.text, response.status_code)
            return response.json()
        else:
            print(f"Файл {filename} не найден, создаётся новый...")
            return self.upload_file(filepath, filename, parent_id)

