from django.db import models
from django.utils.translation import gettext_lazy as _


class PersonType(models.TextChoices):
    PARTNER_MEMBER = "PM", _("PARTNER_MEMBER")
    TICKETING_AGENT = "TA", _("TICKETING_AGENT")
    CUSTOMER = "CR", _("CUSTOMER")
    OWNER = "OW", _("OWNER")


class PartnerPromotionPeriod(models.TextChoices):
    WEEKLY = "WEEKLY", _("WEEKLY")
    MONTHLY = "MONTHLY", _("MONTHLY")
    SINGLE_RUN = "SINGLE_RUN", _("SINGLE_RUN")
