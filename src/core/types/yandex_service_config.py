class YandexServiceConfig:
    def __init__(self, json):
        self._json = json
        self.client_id = json["client_id"]
        self.client_secret = json["client_secret"]

    def __dict__(self):
        return self._json

    def __str__(self):
        return str(self.__dict__())
