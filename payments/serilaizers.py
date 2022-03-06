from rest_framework import serializers

from core.serializers import BaseSerializer, InDBBaseSerializer


class PaymentBaseSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=False)
    person_id = serializers.CharField(max_length=255, required=False)
    made_through = serializers.CharField(max_length=255, required=False)


class PaymentSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    person_id = serializers.CharField(max_length=255)
    made_through = serializers.CharField(max_length=255)


class PaymentCreateSerializer(BaseSerializer, PaymentSerializer):
    pass


class PaymentUpdateSerializer(BaseSerializer, PaymentBaseSerializer):
    pass


class PaymentReadSerializer(InDBBaseSerializer, PaymentBaseSerializer):
    pass
