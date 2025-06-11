import json
from pathlib import Path

from src.core.singleton import Singleton
from src.core.types.app_config import AppConfig
from src.core.types.yandex_service_config import YandexServiceConfig


class ConfigService(metaclass=Singleton):
    def __init__(self, config_path=None):
        base_dir = Path(__file__).parent.parent.parent.resolve()

        default_config_path = base_dir / 'config.json'
        default_yandex_config_path = base_dir / 'yandex_config.json'

        self._config_path = Path(config_path).resolve() if config_path else default_config_path
        self.yandex_config_path = default_yandex_config_path

        self._config = None
        self._yandex_config = None

    def init_configs(self):
        with self._config_path.open('r', encoding='utf-8') as config_file:
            self._config = AppConfig(json.load(config_file))
            print(self._config)

        with self.yandex_config_path.open('r', encoding='utf-8') as yandex_config_file:
            self._yandex_config = YandexServiceConfig(json.load(yandex_config_file))
            print(self._yandex_config)

    def get_config(self) -> AppConfig:
        return self._config

    def get_yandex_config(self) -> YandexServiceConfig:
        return self._yandex_config
