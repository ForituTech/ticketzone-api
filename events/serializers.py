from rest_framework import serializers

from core.serializers import BaseSerializer, InDBBaseSerializer


class EventBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    poster = serializers.CharField(required=False)
    event_date = serializers.DateField(required=False)
    event_location = serializers.CharField(required=False)
    description = serializers.CharField(required=False)


class EventSerializer(BaseSerializer):
    name = serializers.CharField(max_length=256)
    poster = serializers.CharField()
    event_date = serializers.DateField()
    event_location = serializers.CharField()
    description = serializers.CharField()
    partner_id = serializers.CharField(max_length=255)


class EventReadSerializer(InDBBaseSerializer, EventBaseSerializer):
    pass


class EventUpdateSerializer(BaseSerializer, EventBaseSerializer):
    pass


class TicketTypeBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    price = serializers.IntegerField(required=False)
    active = serializers.BooleanField(required=False)
    amsg = serializers.CharField(max_length=256, required=False)
    amount = serializers.IntegerField(required=False)


class TicketTypeSerializer(BaseSerializer):
    name = serializers.CharField(max_length=256)
    price = serializers.IntegerField()
    active = serializers.BooleanField()
    amsg = serializers.CharField()
    amount = serializers.IntegerField()


class TicketTypeCreateSerializer(TicketTypeSerializer):
    event_id = serializers.CharField(max_length=255)


class TicketTypeUpdateSerializer(BaseSerializer, TicketTypeBaseSerializer):
    pass


class TickeTypeReadSerializer(InDBBaseSerializer, TicketTypeBaseSerializer):
    pass


class EventPromotionBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    event_id = serializers.CharField(max_length=255, required=False)
    promotion_rate = serializers.IntegerField(required=False)
    expiry = serializers.DateField(required=False)


class EventPromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    event_id = serializers.CharField(max_length=255)
    promotion_rate = serializers.IntegerField()
    expiry = serializers.DateField()


class EventPromotionUpdateSerializer(BaseSerializer, EventPromotionBaseSerializer):
    pass


class EventPromotionCreateSerializer(BaseSerializer, EventPromotionSerializer):
    pass


class TicketTypePromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    ticket_id = serializers.CharField(max_length=255)
    promotion_rate = serializers.IntegerField()
    expiry = serializers.DateField()


class TicketTypePromotionBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    promotion_rate = serializers.IntegerField(required=False)
    expiry = serializers.DateField(required=False)


class TicketTypePromotionCreateSerializer(
    BaseSerializer, TicketTypePromotionSerializer
):
    pass


class TicketTypePromotionUpdateSerializer(
    BaseSerializer, TicketTypePromotionBaseSerializer
):
    pass
