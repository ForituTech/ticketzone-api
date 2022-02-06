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


class TicketTypeCreateSerializer(BaseSerializer, TicketTypeBaseSerializer):
    event = serializers.UUIDField()


class TicketTypeUpdateSerializer(BaseSerializer, TicketTypeBaseSerializer):
    pass


class TickeTypeReadSerializer(TicketTypeBaseSerializer):
    id = serializers.UUIDField()


class EventPromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    event = serializers.UUIDField()
    promotion_rate = serializers.IntegerField()
    expiry = serializers.DateField()


class EventPromotionUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    promotion_rate = serializers.IntegerField(required=False)
    expiry = serializers.DateField(required=False)


class TicketTypePromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    ticket = serializers.UUIDField()
    promotion_rate = serializers.IntegerField()
    expiry = serializers.DateField()


class TicketTypePromotionUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    promotion_rate = serializers.IntegerField(required=False)
    expiry = serializers.DateField(required=False)
