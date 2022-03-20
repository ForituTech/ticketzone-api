from typing import Any, Dict

from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    def __init__(self, data_in: Dict[Any, Any], *args: Any, **kwargs: Any) -> None:
        self.__dict__ = data_in
        super().__init__(*args, **kwargs)


class BaseInDBSerializer(BaseSerializer):
    id = serializers.CharField(max_length=255)
    created_at = serializers.CharField(max_length=255)
    updated_at = serializers.CharField(max_length=255)


class InDBBaseSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    created_at = serializers.CharField(max_length=255)
    updated_at = serializers.CharField(max_length=255)


class VerifyActionSerializer(serializers.Serializer):
    done = serializers.BooleanField(default=False)


class PromoOptinCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()
