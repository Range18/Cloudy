import json
from pathlib import Path

from src.core.types.app_config import AppConfig
from src.core.types.cloud_services_enum import CloudServices
from src.core.types.yandex_service_config import YandexServiceConfig
from src.core.types.google_service_config import GoogleServiceConfig


class ConfigService:
    _base_dir = Path(__file__).parent.parent.parent.resolve()

    _config_path = _base_dir / 'config.json'
    yandex_config_path = _base_dir / 'yandex_credentials.json'
    google_config_path = _base_dir / 'google_credentials.json'

    _config = None
    _yandex_config = None
    _google_config = None

    @staticmethod
    def init_configs():
        with ConfigService._config_path.open('r', encoding='utf-8') as config_file:
            ConfigService._config = AppConfig(json.load(config_file))

        with ConfigService.yandex_config_path.open('r', encoding='utf-8') as yandex_config_file:
            ConfigService._yandex_config = YandexServiceConfig(json.load(yandex_config_file))

        with ConfigService.google_config_path.open('r', encoding='utf-8') as google_config_file:
            google_data = json.load(google_config_file)
            ConfigService._google_config = GoogleServiceConfig.from_dict(google_data)

    @staticmethod
    def get_google_config() -> GoogleServiceConfig:
        return ConfigService._google_config

    @staticmethod
    def get_config() -> AppConfig:
        return ConfigService._config

    @staticmethod
    def get_yandex_config() -> YandexServiceConfig:
        return ConfigService._yandex_config

    @staticmethod
    def add_service(service: CloudServices):
        with ConfigService._config_path.open('r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)

        services = config_data.get("services", [])
        service_name = service.name

        if service_name not in services:
            services.append(service_name)
            config_data["services"] = services

            with ConfigService._config_path.open('w', encoding='utf-8') as config_file:
                json.dump(config_data, config_file, ensure_ascii=False, indent=2)

            ConfigService._config = AppConfig(config_data)
            print(f"Service '{service_name}' has been added to the config.")

    @staticmethod
    def change_root(path):
        with ConfigService._config_path.open('r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)

        config_data["path"] = path
        config_data["root"] = '/' + Path(path).name

        with ConfigService._config_path.open('w', encoding='utf-8') as config_file:
            json.dump(config_data, config_file, ensure_ascii=False, indent=2)

        ConfigService._config = AppConfig(config_data)
        print(f"Root directory changed to {path}")
