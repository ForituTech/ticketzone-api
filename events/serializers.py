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
    sales = serializers.FloatField()
    event_number = serializers.CharField()


class EventUpdateSerializer(BaseSerializer, EventBaseSerializer):
    pass


class TicketTypeBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    price = serializers.IntegerField(required=False)
    active = serializers.BooleanField(required=False)
    amsg = serializers.CharField(max_length=256, required=False)
    amount = serializers.IntegerField(required=False)


class TicketTypeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    price = serializers.IntegerField()
    active = serializers.BooleanField()
    amsg = serializers.CharField()
    amount = serializers.IntegerField()


class TicketTypeCreateSerializer(BaseSerializer, TicketTypeSerializer):
    event_id = serializers.CharField(max_length=255)


class TicketTypeUpdateSerializer(BaseSerializer, TicketTypeBaseSerializer):
    pass


class TickeTypeReadSerializer(InDBBaseSerializer, TicketTypeBaseSerializer):
    pass


class EventPromotionBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    event_id = serializers.CharField(max_length=255, required=False)
    promotion_rate = serializers.FloatField(required=False)
    expiry = serializers.DateField(required=False)


class EventPromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    event_id = serializers.CharField(max_length=255)
    promotion_rate = serializers.FloatField()
    expiry = serializers.DateField()
    use_limit = serializers.IntegerField()


class EventPromotionUpdateSerializer(BaseSerializer, EventPromotionBaseSerializer):
    pass


class EventPromotionCreateSerializer(BaseSerializer, EventPromotionSerializer):
    pass


class EventPromotionReadSerializer(InDBBaseSerializer, EventPromotionSerializer):
    pass


class TicketTypePromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    ticket_id = serializers.CharField(max_length=255)
    promotion_rate = serializers.FloatField()
    expiry = serializers.DateField()


class TicketTypePromotionBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    promotion_rate = serializers.FloatField(required=False)
    expiry = serializers.DateField(required=False)


class TicketTypePromotionCreateSerializer(
    BaseSerializer, TicketTypePromotionSerializer
):
    pass


class TicketTypePromotionUpdateSerializer(
    BaseSerializer, TicketTypePromotionBaseSerializer
):
    pass


class TicketTypePromotionReadSerializer(
    InDBBaseSerializer, TicketTypePromotionSerializer
):
    pass


class PromoVerifySerializer(BaseSerializer):
    target_ids = serializers.ListField(child=serializers.CharField(max_length=255))


class PromoVerifyInnerSerializer(serializers.Serializer):
    target_ids = serializers.ListField(child=serializers.CharField(max_length=255))


class PromotionSerializer(serializers.Serializer):
    rate = serializers.FloatField()
    target_id = serializers.CharField(max_length=255)


class CategorySerializer(InDBBaseSerializer, serializers.Serializer):
    name = serializers.CharField(max_length=255)


class CategoryInnerSerializer(BaseSerializer, CategorySerializer):
    pass


class EventWithSales(EventReadSerializer):
    sales = serializers.FloatField()


class TicketTypeWithSales(TickeTypeReadSerializer):
    sales = serializers.FloatField()
