from typing import Optional

from partner.fixtures.partner_fixtures import create_partner_obj
from partner.models import Partner, Person
from partner_api.models import ApiCredentials


def create_partner_api_credentials_obj(
    partner: Optional[Partner] = None, owner: Optional[Person] = None
) -> ApiCredentials:
    partner = partner or create_partner_obj(owner=owner)
    api_creds = ApiCredentials.objects.create(**{"partner": partner})
    api_creds.save()
    return api_creds
