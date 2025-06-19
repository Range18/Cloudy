class AppConfig:
    def __init__(self, json):
        self._json = json
        self.path = json['path']
        self.services = json['services']

    def __dict__(self):
        return self._json

    def __str__(self):
        return str(self.__dict__())
