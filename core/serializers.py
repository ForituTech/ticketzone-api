from typing import Any, Dict, Optional

from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    def __init__(self, data_in: Optional[Dict[Any, Any]], *args, **kwargs):
        self.__dict__ = data_in
        super().__init__(*args, **kwargs)
