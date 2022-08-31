from rest_framework import serializers

from core.serializers import BaseSerializer, InDBBaseSerializer


class TicketTypeBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    price = serializers.IntegerField(required=False)
    active = serializers.BooleanField(required=False)
    amsg = serializers.CharField(max_length=256, required=False)
    amount = serializers.IntegerField(required=False)
    is_visible = serializers.BooleanField(required=False, default=True)
    use_limit = serializers.IntegerField(required=False, default=1)


class TicketTypeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    price = serializers.IntegerField()
    active = serializers.BooleanField()
    amsg = serializers.CharField()
    amount = serializers.IntegerField()
    is_visible = serializers.BooleanField(required=False, default=True)
    use_limit = serializers.IntegerField(required=False, default=1)


class TicketTypeCreateSerializer(BaseSerializer, TicketTypeSerializer):
    event_id = serializers.CharField(max_length=255)


class TicketTypeUpdateSerializer(BaseSerializer, TicketTypeBaseSerializer):
    pass


class TickeTypeReadSerializer(InDBBaseSerializer, TicketTypeSerializer):
    pass


class EventPromotionBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    event_id = serializers.CharField(max_length=255, required=False)
    promotion_rate = serializers.FloatField(required=False)
    expiry = serializers.DateField(required=False)


class EventPromotionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    promotion_rate = serializers.FloatField()
    expiry = serializers.DateField()
    use_limit = serializers.IntegerField()


class EventPromotionUpdateSerializer(BaseSerializer, EventPromotionBaseSerializer):
    pass


class EventPromotionCreateSerializer(BaseSerializer, EventPromotionSerializer):
    event_id = serializers.CharField(max_length=255)


class EventPromotionReadSerializer(InDBBaseSerializer, EventPromotionSerializer):
    event_id = serializers.CharField(max_length=255)


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


class TicketTypeWithSales(TickeTypeReadSerializer):
    sales = serializers.FloatField()


class EventBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    poster = serializers.ImageField(required=False)
    event_date = serializers.DateField(required=False)
    time = serializers.TimeField(required=False)
    event_end_date = serializers.DateField(required=False)
    end_time = serializers.TimeField(required=False)
    event_location = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    ticket_types = serializers.ListField(
        child=TickeTypeReadSerializer(), max_length=100, required=False
    )


class EventSerializer(BaseSerializer):
    name = serializers.CharField(max_length=256)
    poster = serializers.ImageField()
    event_date = serializers.DateField()
    time = serializers.TimeField()
    event_end_date = serializers.DateField()
    end_time = serializers.TimeField()
    event_location = serializers.CharField()
    description = serializers.CharField()
    partner_id = serializers.CharField(max_length=255)
    partner_person_ids = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False
    )
    ticket_types = serializers.ListField(
        child=TicketTypeSerializer(), max_length=100, required=False
    )
    event_promotions = serializers.ListField(
        child=EventPromotionSerializer(), max_length=10, required=False
    )


class EventReadSerializer(InDBBaseSerializer, EventBaseSerializer):
    from partner.serializers import PartnerPersonReadSerializer

    event_number = serializers.CharField()
    event_state = serializers.CharField()
    tickets_sold = serializers.IntegerField()
    redemption_rate = serializers.FloatField()
    sales = serializers.FloatField()
    assigned_ticketing_agents = serializers.ListField(
        child=PartnerPersonReadSerializer(), max_length=10
    )
    ticket_types = serializers.ListField(
        child=TickeTypeReadSerializer(), max_length=100, required=False
    )


class EventUpdateSerializer(BaseSerializer, EventBaseSerializer):
    partner_person_ids = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False
    )
    ticket_types = serializers.ListField(
        child=TicketTypeSerializer(), max_length=100, required=False
    )
    event_promotions = serializers.ListField(
        child=EventPromotionSerializer(), max_length=10, required=False
    )


class EventWithSales(EventReadSerializer):
    sales = serializers.FloatField()
