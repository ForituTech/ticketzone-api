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
    amount = serializers.FloatField()


class EventLiteSerializer(serializers.Serializer):
    event_number = serializers.CharField()
    name = serializers.CharField(max_length=255)
    poster = serializers.ImageField()


class TicketTypeLiteSerializer(serializers.Serializer):
    name = serializers.CharField()
    event = EventLiteSerializer()


class TicketReadSerializer(InDBBaseSerializer, TicketSerializer):
    ticket_number = serializers.CharField()
    redeemed = serializers.BooleanField()
    sent = serializers.BooleanField()
    uses = serializers.IntegerField()
    valid = serializers.CharField()
    payment = PaymentLiteSerializer()
    ticket_type = TicketTypeLiteSerializer()


class CountAtDate(serializers.Serializer):
    count = serializers.IntegerField()
    date = serializers.CharField(max_length=255)


class TotalSalesOverTime(serializers.Serializer):
    data = serializers.ListField(child=CountAtDate())  # type: ignore


class TicketScanBaseSerializer(serializers.Serializer):
    agent_id = serializers.CharField(max_length=255)
    ticket_id = serializers.CharField(max_length=255)
    redeem_triggered = serializers.BooleanField(default=False)


class TicketScanCreateSerializer(TicketScanBaseSerializer, BaseSerializer):
    pass


class TicketScanSerializer(InDBBaseSerializer, TicketScanBaseSerializer):
    ticket = TicketReadSerializer()
