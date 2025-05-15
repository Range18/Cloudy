class HttpException(Exception):
    def __init__(self, message, code, details=None):
        self.message = message
        self.code = code
        self.details = details
        super(HttpException, self).__init__(message)

    def __str__(self):
        return str(self.__dict__)
