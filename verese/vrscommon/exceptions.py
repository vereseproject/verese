class APIException(Exception):
    def __init__(self, error, code='NOT_IMPLEMENTED'):
        self.error = error
        self.code = code

class APIBadRequest(APIException):
    def __init__(self, error):
        super(APIBadRequest, self).__init__(error, 'BAD_REQUEST')

class APIForbidden(APIException):
    def __init__(self, error):
        super(APIForbidden, self).__init__(error, 'FORBIDDEN')

class APINotFound(APIException):
    def __init__(self, error):
        super(APINotFound, self).__init__(error, 'NOT_FOUND')

