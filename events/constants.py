from django.db import models
from django.utils.translation import gettext_lazy as _


class EventState(models.TextChoices):
    PRE_REVIEW = "PR", _("PRE_REVIEW")
    ACTIVE = "AE", _("ACTIVE")
    PRE_CLOSED = "PC", _("PRE_CLOSED")
    CLOSED = "CD", _("CLOSED")
