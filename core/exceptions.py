import uuid
from typing import Union

from rest_framework import status
from rest_framework.exceptions import APIException

from core.error_codes import ErrorCodes


class ObjectNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, model: str, pk: Union[uuid.UUID, str]):
        super().__init__(detail=f"{model} with id: {pk} not found", code="not_found")


class ObjectInvalidException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, model: str):
        super().__init__(
            detail=f"Couldn't construct an instance of {model} with the provided data",
            code="unprocessable_entity",
        )


class HttpErrorException(APIException):
    def __init__(self, status_code: int, code: ErrorCodes) -> None:
        self.status_code = status_code
        super().__init__(detail=f"{code.name}: {code.value}", code=code.value)
