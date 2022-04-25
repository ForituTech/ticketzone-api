from rest_framework import serializers

from core.serializers import BaseSerializer, InDBBaseSerializer
from partner.serializers import PersonSerializer


class TicketBaseSerialier(serializers.Serializer):
    ticket_type_id = serializers.CharField(max_length=255, required=False)
    payment_id = serializers.CharField(max_length=255, required=False)


class TicketSerializer(serializers.Serializer):
    ticket_type_id = serializers.CharField(max_length=255)
    payment_id = serializers.CharField(max_length=255)


class TicketCreateSerializer(BaseSerializer, TicketSerializer):
    pass


class TicketUpdateSerializer(serializers.Serializer):
    redeemed = serializers.BooleanField(default=False)


class TicketUpdateInnerSerializer(BaseSerializer, TicketUpdateSerializer):
    pass


class PaymentLiteSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=255)
    person = PersonSerializer()


class TicketReadSerializer(InDBBaseSerializer, TicketSerializer):
    redeemed = serializers.BooleanField()
    sent = serializers.BooleanField()
    uses = serializers.IntegerField()
    payment = PaymentLiteSerializer()


class CountAtDate(serializers.Serializer):
    count = serializers.IntegerField()
    date = serializers.CharField(max_length=255)


class TotalSalesOverTime(serializers.Serializer):
    data = serializers.ListField(child=CountAtDate())  # type: ignore
