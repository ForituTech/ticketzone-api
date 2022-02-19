from typing import Any, Dict

from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    def __init__(self, data_in: Dict[Any, Any], *args: Any, **kwargs: Any) -> None:
        self.__dict__ = data_in
        super().__init__(*args, **kwargs)
