from django.db import models

from partner.models import Partner


class Event(models.Model):
    name = models.CharField(
        max_length=256, null=False, blank=False, default="new-event"
    )
    poster = models.ImageField(null=False, blank=False, upload_to="media/")
    event_date = models.DateField(null=True, blank=True, auto_now=False)
    event_location = models.CharField(max_length=1024, null=True, blank=True)
    description = models.CharField(max_length=1024, null=False, blank=False)
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=False, blank=False
    )
    is_public = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        verbose_name="Has the event been published",
    )

    def __str__(self) -> str:
        return self.name


class TicketType(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)
    amsg = models.CharField(
        verbose_name="Active Message",
        max_length=256,
        null=False,
        blank=False,
        default="Open Soon",
    )
    amount = models.IntegerField(null=False, blank=False, default=100)
    is_visible = models.BooleanField(
        null=False, blank=False, default=True, verbose_name="Is Ticket Visible To Users"
    )

    def __str__(self) -> str:
        return "{0} - {1}".format(self.event.name, self.name)


class EventPromotion(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False)
    promotion_rate = models.IntegerField(null=False, blank=False, default=100)
    expiry = models.DateField(null=False, blank=False, auto_now=False)

    def __str__(self) -> str:
        return self.name


class TicketPromotion(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    ticket = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, null=False, blank=False
    )
    promotion_rate = models.IntegerField(null=False, blank=False, default=100)
    expiry = models.DateField(null=False, blank=False, auto_now=False)

    def __str__(self) -> str:
        return self.name
