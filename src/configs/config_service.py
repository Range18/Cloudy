import json

from src.core.types.app_config import AppConfig


class ConfigService:
    def __init__(self, config_path=None):
        self._config_path = config_path if config_path else 'config.json'
        self._config = None

    def init_config(self):
        with open(self._config_path, 'r') as config:
            self._config = AppConfig(json.load(config))
            print(self._config)

    def get_config(self) -> AppConfig:
        return self._config
