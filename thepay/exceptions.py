class ThePayException(Exception):
    pass


class MissingParameter(ThePayException):
    pass


class InvalidSignature(ThePayException):
    pass
