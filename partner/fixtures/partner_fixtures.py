from partner.models import Partner, PartnerBankingInfo, Person

person_fixture = {
    "name": "Nelson Mongare",
    "email": "nelsonmongare@protonmail.com",
    "phone_number": "254799762765",
    "person_type": "PR",
    "hashed_password": "123456",
}

partner_banking_info_fixture = {
    "bank_code": 123456,
    "bank_account_number": 1234567891234657899,
}

partner_fixture = {
    "name": "Muze Ticketing",
    "owner": "ad85e010-d24b-491e-b06c-c1bd77c87642",
    "banking_info": "f153d108-e16b-4bc4-bc6f-0735a8d38f61",
}


def create_person_obj() -> Person:
    person: Person = Person.objects.create(**person_fixture)
    return person


def create_banking_info_obj() -> PartnerBankingInfo:
    banking_info: PartnerBankingInfo = PartnerBankingInfo.objects.create(
        **partner_banking_info_fixture
    )
    return banking_info


def create_partner_obj() -> Partner:
    data = partner_fixture.copy()
    data["banking_info"] = create_banking_info_obj()  # type: ignore
    data["owner"] = create_person_obj()  # type: ignore
    partner: Partner = Partner.objects.create(**data)
    return partner
