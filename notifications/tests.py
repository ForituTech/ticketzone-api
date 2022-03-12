from typing import Any
from unittest import mock

from django.test import TestCase

from eticketing_api.utils import random_string
from notifications.pusher import pusher_client
from notifications.sms import sms_client
from notifications.utils import send_push_notification, send_sms
from partner.fixtures import partner_fixtures


class NotificationsTestCase(TestCase):
    def setUp(self) -> None:
        self.person = partner_fixtures.create_person_obj()

    @mock.patch.object(sms_client, "send")
    def test_send_sms(self, mock_sms_client: Any) -> None:
        message = random_string()
        send_sms(self.person, message)

        mock_sms_client.assert_called_with(message, [self.person.phone_number])

    @mock.patch.object(pusher_client, "push_web_notification")
    def test_send_push_notification(self, mock_pusher_client: Any) -> None:
        mock_pusher_client.return_value = {"publishId": random_string()}
        message = random_string()
        send_push_notification(self.person, message, {message: message})

        mock_pusher_client.assert_called_with(
            user_ids=[str(self.person.id)], body=message, data={message: message}
        )
