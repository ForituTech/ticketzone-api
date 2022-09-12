from datetime import date, timedelta
from typing import Any
from unittest import mock
from unittest.mock import ANY

from django.test import TestCase

from core.utils import random_string
from eticketing_api import settings
from events.models import Ticket
from notifications.fixtures import notification_fixtures
from notifications.models import Notification
from notifications.pusher import pusher_client
from notifications.sms import sms_client
from notifications.tasks import cleanup_notifications
from notifications.utils import send_push_notification, send_sms, send_ticket_email
from partner.fixtures import partner_fixtures
from tickets.fixtures import ticket_fixtures


class NotificationsTestCase(TestCase):
    def setUp(self) -> None:
        self.person = partner_fixtures.create_person_obj()

    @mock.patch.object(sms_client, "send")
    def test_send_sms(self, mock_sms_client: Any) -> None:
        message = random_string()
        send_sms(self.person.id, message)

        mock_sms_client.assert_called_with(message, [self.person.phone_number])

    @mock.patch.object(pusher_client, "push_web_notification")
    def test_send_push_notification(self, mock_pusher_client: Any) -> None:
        mock_pusher_client.return_value = {"publishId": random_string()}
        message = random_string()
        send_push_notification(self.person, message, {message: message})

        mock_pusher_client.assert_called_with(
            user_ids=[str(self.person.id)], body=message, data={message: message}
        )

    @mock.patch("requests.get")
    @mock.patch("notifications.utils.EmailMessage")
    def test_send_ticket_email(
        self, mock_email_service: Any, mock_get_response: Any
    ) -> None:
        mock_get_response.return_value = notification_fixtures.MockResp()
        mock_email_object = mock_email_service.return_value
        ticket: Ticket = ticket_fixtures.create_ticket_obj()

        send_ticket_email(str(ticket.id))

        mock_email_service.assert_called_with(
            subject=settings.TICKET_EMAIL_TITLE,
            to=(ticket.payment.person.email,),
            attachments=[ANY],
            body=settings.TICKET_EMAIL_BODY.format(ticket.payment.person.name),
        )

        mock_email_object.send.return_value = 0
        mock_email_object.send.assert_called_with(fail_silently=True)

    def test_cleanup_old_notifications(self) -> None:
        notification: Notification = notification_fixtures.create_notification_obj()
        notification.created_at = date.today() - timedelta(weeks=2)
        notification.save()
        notification_id = str(notification.id)
        notification2: Notification = notification_fixtures.create_notification_obj()

        cleanup_notifications()

        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(pk=notification_id)

        notification2.refresh_from_db()
        assert notification2
