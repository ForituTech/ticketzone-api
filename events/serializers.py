from rest_framework import serializers

from core.serializers import BaseSerializer


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
    partner = serializers.UUIDField()


class EventReadSerializer(EventBaseSerializer):
    id = serializers.UUIDField()


class EventUpdateSerializer(BaseSerializer, EventBaseSerializer):
    pass


class TicketTypeBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    price = serializers.IntegerField(required=False)
    active = serializers.BooleanField(required=False)
    inactive_msg = serializers.CharField(max_length=256, required=False)
    amount = serializers.IntegerField(required=False)


class TicketTypeSerializer(BaseSerializer):
    name = serializers.CharField(max_length=256)
    price = serializers.IntegerField()
    active = serializers.BooleanField()
    inactive_msg = serializers.CharField()
    amount = serializers.IntegerField()


class TicketTypeCreateSerializer(TicketTypeSerializer):
    event = serializers.UUIDField()


class TicketTypeUpdateSerializer(BaseSerializer, TicketTypeBaseSerializer):
    pass


class TickeTypeReadSerializer(TicketTypeBaseSerializer):
    id = serializers.UUIDField()


class EventPromotionBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    event = serializers.UUIDField(required=False)
    promotion_rate = serializers.IntegerField(required=False)
    expiry = serializers.DateField(required=False)


class EventPromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    event = serializers.UUIDField()
    promotion_rate = serializers.IntegerField()
    expiry = serializers.DateField()


class EventPromotionUpdateSerializer(BaseSerializer, EventPromotionBaseSerializer):
    pass


class EventPromotionCreateSerializer(BaseSerializer, EventPromotionSerializer):
    pass


class TicketTypePromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    ticket = serializers.UUIDField()
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
