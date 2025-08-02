from fastapi import HTTPException, status


class TgWebAppException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = ""

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(TgWebAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "User already exists"


class UserNotFoundException(TgWebAppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"


class InvalidTelegramIdOrPasswordException(TgWebAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid telegram id or password"


class ForbiddenException(TgWebAppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Forbidden"


class NotAuthenticatedException(TgWebAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authenticated"


class TokenExpiredException(TgWebAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token expired"


class TokenAbsentException(TgWebAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token absent"


class IncorrectTokenFormatException(TgWebAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect token format"


class InvalidRefreshTokenException(TgWebAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid refresh token"
