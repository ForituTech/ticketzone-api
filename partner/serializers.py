from typing import Any

from rest_framework import serializers

from core.serializers import BaseSerializer, InDBBaseSerializer
from partner.utils import random_password, validate_email, validate_phonenumber


class PersonBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    email = serializers.CharField(max_length=255, required=False)
    phone_number = serializers.CharField(max_length=15, required=False)
    person_type = serializers.CharField(max_length=255, required=False)
    hashed_password = serializers.CharField(default=random_password(), required=False)

    def validate_email(self, email: str) -> Any:
        if not validate_email(email):
            raise serializers.ValidationError("Email is invalid")
        return email

    def validate_phone_number(self, phone: str) -> Any:
        if not validate_phonenumber(phone):
            raise serializers.ValidationError("Phonenumber is invalid")
        return phone


class PersonSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    email = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=30)

    def validate_email(self, email: str) -> Any:
        if not validate_email(email):
            raise serializers.ValidationError("Email is invalid")
        return email

    def validate_phone_number(self, phone: str) -> Any:
        if not validate_phonenumber(phone):
            raise serializers.ValidationError("Phonenumber is invalid")
        return phone


class PersonReadSerializer(InDBBaseSerializer, PersonBaseSerializer):
    pass


class PersonCreateSerializer(BaseSerializer, PersonSerializer):
    hashed_password = serializers.CharField()


class PersonUpdateSerializer(BaseSerializer, PersonBaseSerializer):
    pass


class PartnerBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    contact_person = serializers.CharField(required=False)
    bank_code = serializers.CharField(required=False, max_length=255)
    bank_account_number = serializers.CharField(required=False, max_length=512)


class PartnerSerializer(BaseSerializer):
    name = serializers.CharField(max_length=255)
    owner = serializers.CharField()
    contact_person = serializers.CharField(required=False)
    bank_code = serializers.CharField(max_length=255)
    bank_account_number = serializers.CharField(max_length=512)


class PartnerReadSerializer(InDBBaseSerializer, PartnerBaseSerializer):
    owner = serializers.CharField(required=False)


class PartnerUpdateSerializer(BaseSerializer, PartnerBaseSerializer):
    pass


class UserSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()


class PartnerPersonBaseSerializer(serializers.Serializer):
    person_type = serializers.CharField(required=False, max_length=255)
    is_active = serializers.BooleanField(required=False)
    is_hidden = serializers.BooleanField(required=False)


class PartnerPersonCreateSerializer(BaseSerializer, PartnerPersonBaseSerializer):
    person_id = serializers.CharField(max_length=255)
    partner_id = serializers.CharField(max_length=255)


class PartnerPersonUpdateSerializer(BaseSerializer, PartnerPersonBaseSerializer):
    pass


class PartnerPersonSerializer(BaseSerializer, PartnerPersonBaseSerializer):
    person_id = serializers.CharField(max_length=255)
    partner_id = serializers.CharField(max_length=255)


class PartnerPersonReadSerializer(InDBBaseSerializer, PartnerPersonBaseSerializer):
    person = PersonReadSerializer()
    partner_id = serializers.CharField(max_length=255)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)


class SalesSerializer(serializers.Serializer):
    sales = serializers.IntegerField()


class RevenuesSerializer(serializers.Serializer):
    revenue = serializers.FloatField()
    expenses = serializers.FloatField()
    net = serializers.FloatField()


class RedemtionRateSerializer(serializers.Serializer):
    rate = serializers.FloatField()


class PartnerSMSPackageBaseSerializer(serializers.Serializer):
    pass


class PartnerSMSPackageSerializer(serializers.Serializer):
    partner_id = serializers.CharField(max_length=255)


class PartnerSMSPackageReadSerializer(
    InDBBaseSerializer, PartnerSMSPackageBaseSerializer
):
    partner_id = serializers.CharField(max_length=255)
    per_sms_rate = serializers.FloatField()
    sms_limit = serializers.IntegerField()
    sms_used = serializers.IntegerField()
    verified = serializers.BooleanField()


class PartnerSMSPackageUpdateSerializer(
    BaseSerializer, PartnerSMSPackageBaseSerializer
):
    pass


class PartnerSMSPackageCreateSerializer(BaseSerializer, PartnerSMSPackageSerializer):
    pass


class PartnerPromoBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    message = serializers.CharField(max_length=10240, required=False)


class PartnerPromoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    partner_id = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=10240)
    starts_on = serializers.DateField()
    stops_on = serializers.DateField()


class PartnerPromoReadSerializer(InDBBaseSerializer, PartnerPromoSerializer):
    repeat = serializers.CharField(max_length=255)
    last_run = serializers.DateField()
    verified = serializers.BooleanField()


class PartnerPromoUpdateSerializer(PartnerPromoBaseSerializer, BaseSerializer):
    pass


class PartnerPromoCreateSerializer(BaseSerializer, PartnerPromoSerializer):
    pass
