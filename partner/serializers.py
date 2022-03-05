from rest_framework import serializers

from core.serializers import BaseSerializer, InDBBaseSerializer
from partner.utils import random_password


class PersonBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256, required=False)
    email = serializers.CharField(max_length=255, required=False)
    phone_number = serializers.CharField(max_length=15, required=False)
    person_type = serializers.CharField(max_length=255, required=False)
    hashed_password = serializers.CharField(default=random_password(), required=False)


class PersonSerializer(BaseSerializer):
    name = serializers.CharField(max_length=256)
    email = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=30)


class PersonReadSerializer(InDBBaseSerializer, PersonBaseSerializer):
    pass


class PersonCreateSerializer(PersonSerializer):
    hashed_password = serializers.CharField()


class PersonUpdateSerializer(BaseSerializer, PersonBaseSerializer):
    pass


class PartnerBankingInfoSerializer(serializers.Serializer):
    bank_code = serializers.IntegerField(required=False)
    bank_account_number = serializers.IntegerField(required=False)


class PartnerBaseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    owner = serializers.CharField(required=False)
    contact_person = serializers.CharField(required=False)
    banking_info = PartnerBankingInfoSerializer(required=False)


class PartnerSerializer(BaseSerializer):
    name = serializers.CharField(max_length=255)
    owner = serializers.CharField()
    contact_person = serializers.CharField(required=False)
    banking_info = PartnerBankingInfoSerializer()


class PartnerReadSerializer(InDBBaseSerializer, PartnerBaseSerializer):
    pass


class PartnerUpdateSerializer(BaseSerializer, PartnerBaseSerializer):
    banking_info_id = serializers.CharField(max_length=255, required=False)


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
    person_id = serializers.CharField(max_length=255)
    partner_id = serializers.CharField(max_length=255)
