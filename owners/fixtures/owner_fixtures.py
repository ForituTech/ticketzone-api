from typing import Dict, Optional

from core.utils import random_string
from owners.models import Owner
from partner.fixtures.partner_fixtures import random_phone_number


def owner_fixture(stake: Optional[float] = 21.5) -> Dict:
    return {
        "name": random_string(),
        "stake": stake,
        "phone_number": random_phone_number(),
    }


def create_owner_obj(stake: Optional[float] = 21.5) -> Owner:
    data = owner_fixture(stake)
    return Owner.objects.create(**data)
