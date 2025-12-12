from dataclasses import dataclass
from typing import List


@dataclass
class Installed:
    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: List[str]


@dataclass
class GoogleServiceConfig:
    installed: Installed

    @staticmethod
    def from_dict(data: dict) -> "GoogleServiceConfig":
        installed_data = data.get("installed", {})
        installed = Installed(**installed_data)
        return GoogleServiceConfig(installed=installed)
