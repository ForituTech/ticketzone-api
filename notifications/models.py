from django.db import models

from core.models import BaseModel
from notifications.constants import NotificationsChannels
from partner.models import Person


class Notification(BaseModel):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=False, blank=False
    )
    message = models.CharField(max_length=2048, null=False, blank=False)
    channel = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        default=NotificationsChannels.EMAIL.value,
    )
    has_data = models.BooleanField(null=False, blank=False, default=True)
    sent = models.BooleanField(null=False, blank=False, default=False)


class MassNotification(BaseModel):
    people = models.ManyToManyField(Person)
    channel = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        default=NotificationsChannels.EMAIL.value,
    )
    has_data = models.BooleanField(null=False, blank=False, default=True)
    sent = models.BooleanField(null=False, blank=False, default=False)
