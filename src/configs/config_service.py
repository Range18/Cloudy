import json


class ConfigService:
    def __init__(self, config_path=None):
        self._config_path = config_path if config_path else 'config.json'

    def init_config(self):
        with open(self._config_path, 'r') as config:
            print(json.load(config))
