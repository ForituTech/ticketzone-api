from rest_framework import status
from rest_framework.exceptions import APIException


class ObjectNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, model: str, pk: int):
        super().__init__(detail=f"{model} with pk: {pk} not found", code="not_found")
