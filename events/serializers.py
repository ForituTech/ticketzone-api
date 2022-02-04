from rest_framework import serializers


class EventSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    poster = serializers.CharField()
    event_date = serializers.DateField()
    event_location = serializers.CharField()
    description = serializers.CharField()
    partner = serializers.IntegerField()


class EventUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    poster = serializers.CharField(required=False)
    event_date = serializers.DateField(required=False)
    event_location = serializers.CharField(required=False)
    description = serializers.CharField(required=False)


class EventReadSerializer(EventUpdateSerializer):
    pass


class TicketTypeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    price = serializers.IntegerField()
    event = serializers.IntegerField()
    active = serializers.BooleanField()
    inactive_msg = serializers.CharField(max_length=256)
    amount = serializers.IntegerField()
    is_visible = serializers.BooleanField()


class TicketTypeUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    price = serializers.IntegerField(required=False)
    active = serializers.BooleanField(required=False)
    inactive_msg = serializers.CharField(max_length=256, required=False)
    amount = serializers.IntegerField(required=False)
    is_visible = serializers.BooleanField(required=False)


class EventPromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    event = serializers.IntegerField()
    promotion_rate = serializers.IntegerField()
    expiry = serializers.DateField()


class EventPromotionUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    promotion_rate = serializers.IntegerField(required=False)
    expiry = serializers.DateField(required=False)


class TicketTypePromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    ticket = serializers.IntegerField()
    promotion_rate = serializers.IntegerField()
    expiry = serializers.DateField()


class TicketTypePromotionUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    promotion_rate = serializers.IntegerField(required=False)
    expiry = serializers.DateField(required=False)
