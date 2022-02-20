from rest_framework import serializers

from core.serializers import BaseSerializer
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
    phone_number = serializers.CharField(max_length=15)
    person_type = serializers.CharField(max_length=255)


class PersonReadSerializer(PersonBaseSerializer):
    id = serializers.UUIDField()


class PersonCreateSerializer(PersonSerializer):
    hashed_password = serializers.CharField()


class PersonUpdateSerializer(BaseSerializer, PersonBaseSerializer):
    pass


class PartnerBankingInfoSerializer(serializers.Serializer):
    bank_code = serializers.IntegerField()
    bank_account_number = serializers.IntegerField()


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


class PertnerReadSerializer(PartnerBaseSerializer):
    id = serializers.UUIDField()


class PartnerUpdateSerializer(BaseSerializer, PartnerBaseSerializer):
    pass


class UserSerializer(serializers.Serializer):
    phonenumber = serializers.CharField()
    password = serializers.CharField()
