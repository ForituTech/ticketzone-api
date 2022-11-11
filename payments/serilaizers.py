from rest_framework import serializers

from core.serializers import BaseSerializer, InDBBaseSerializer
from partner.serializers import PersonSerializer


class PaymentBaseSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=False)
    person_id = serializers.CharField(max_length=255, required=False)
    made_through = serializers.CharField(max_length=255, required=False)


class PaymentSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    person_id = serializers.CharField(max_length=255)
    made_through = serializers.CharField(max_length=255)


class TicketTypeSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)
    amount = serializers.IntegerField(min_value=1)


class PaymentCreateSerializerInner(BaseSerializer):
    amount = serializers.FloatField()
    made_through = serializers.CharField(max_length=255)
    person_id = serializers.CharField(max_length=255)
    ticket_types = serializers.ListField(child=TicketTypeSerializer())


class PaymentCreateSerializer(serializers.Serializer):
    made_through = serializers.CharField(max_length=255)
    person = PersonSerializer()
    ticket_types = serializers.ListField(child=TicketTypeSerializer())


class PaymentUpdateSerializer(BaseSerializer, PaymentBaseSerializer):
    pass


class PaymentReadSerializer(InDBBaseSerializer, PaymentBaseSerializer):
    pass


class PaymentMethodSerialzier(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    poster = serializers.ImageField(required=False)


class PaymentMethodWriteSerializer(BaseSerializer, PaymentMethodSerialzier):
    pass
