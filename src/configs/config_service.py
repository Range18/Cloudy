import json
from pathlib import Path

from src.core.singleton import Singleton
from src.core.types.app_config import AppConfig
from src.core.types.cloud_services_enum import CloudServices
from src.core.types.yandex_service_config import YandexServiceConfig
from src.core.types.google_service_config import GoogleServiceConfig


class ConfigService(metaclass=Singleton):
    def __init__(self, config_path=None):
        base_dir = Path(__file__).parent.parent.parent.resolve()

        default_config_path = base_dir / 'config.json'
        default_yandex_config_path = base_dir / 'yandex_credentials.json'
        default_google_config_path = base_dir / 'google_credentials.json'

        self._config_path = Path(config_path).resolve() if config_path else default_config_path
        self.yandex_config_path = default_yandex_config_path
        self.google_config_path = default_google_config_path

        self._config = None
        self._yandex_config = None
        self._google_config = None

    def init_configs(self):
        with self._config_path.open('r', encoding='utf-8') as config_file:
            self._config = AppConfig(json.load(config_file))

        with self.yandex_config_path.open('r', encoding='utf-8') as yandex_config_file:
            self._yandex_config = YandexServiceConfig(json.load(yandex_config_file))

        with self.google_config_path.open('r', encoding='utf-8') as google_config_file:
            google_data = json.load(google_config_file)
            self._google_config = GoogleServiceConfig.from_dict(google_data)

    def get_google_config(self) -> GoogleServiceConfig:
        return self._google_config

    def get_config(self) -> AppConfig:
        return self._config

    def get_yandex_config(self) -> YandexServiceConfig:
        return self._yandex_config

    def add_service(self, service: CloudServices):
        with self._config_path.open('r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)

        services = config_data.get("services", [])
        service_name = service.name

        if service_name not in services:
            services.append(service_name)
            config_data["services"] = services

            with self._config_path.open('w', encoding='utf-8') as config_file:
                json.dump(config_data, config_file, ensure_ascii=False, indent=2)

            self._config = AppConfig(config_data)
            print(f"Сервис '{service_name}' добавлен в конфиг.")
        else:
            print(f"Сервис '{service_name}' уже существует в конфиге.")



