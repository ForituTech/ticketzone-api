from typing import Dict, Optional

from core.utils import random_string
from notifications.constants import NotificationsChannels
from notifications.models import Notification
from partner.fixtures import partner_fixtures
from partner.models import Person


class MockResp:
    def __init__(self) -> None:
        self.content = open("media/42_EluV6G9.jpg", "rb").read()


def notification_fixture(
    person_id: Optional[str] = None, channel: Optional[NotificationsChannels] = None
) -> Dict:
    return {
        "person_id": person_id
        if person_id
        else str(partner_fixtures.create_person_obj().id),
        "message": random_string(),
        "channel": channel.value if channel else NotificationsChannels.SMS.value,
    }


def create_notification_obj(
    person: Optional[Person] = None, channel: Optional[NotificationsChannels] = None
) -> Notification:
    data = notification_fixture(
        person_id=str(person.id) if person else None, channel=channel
    )
    return Notification.objects.create(**data)
