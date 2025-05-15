import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from src.app.yandex.yandex_disk_api_service import YandexDiskApiService


class CloudService:
    def __init__(self):
        self.yandex_api_service = YandexDiskApiService()

    def authenticate(self):
        pass

    def authenticate_google(self):
        SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("../../token.json"):
            creds = Credentials.from_authorized_user_file("../../token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "../../credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("../../token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def download_file(self, path):
        pass

    def create_file(self, path, destination, overwrite=False):
        self.yandex_api_service.upload_file(path, destination, overwrite)

    def make_dir(self, path):
        self.yandex_api_service.make_dir(path)

    def remove_file_or_dir(self, path):
        self.yandex_api_service.remove_file_or_dir(path)

    def update(self, path, destination, overwrite=False):
        pass
