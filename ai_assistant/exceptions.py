class AppException(Exception):  # noqa: N818
    pass


class NotFoundException(AppException):
    pass


class AuthorizationException(AppException):
    pass


class InvalidJwt(AuthorizationException):
    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = 'Could not validate credentials'
        super().__init__(message)
