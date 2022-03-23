from django.db import models


class Owner(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    stake = models.FloatField(null=False, blank=False, default=0.0)
    phone_number = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self) -> str:
        return self.name
