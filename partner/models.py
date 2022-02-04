from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    email = models.CharField(
        verbose_name="E-mail", max_length=256, null=False, blank=False, default="0"
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class PartnerBankingInfo(models.Model):
    bank_code = models.IntegerField(null=False, blank=False)
    bank_account_number = models.IntegerField(null=False, blank=False)

    def __str__(self) -> str:
        return f"Banking info"


class Partner(models.Model):
    contact_person = models.ForeignKey(
        Person, on_delete=models.SET_NULL, null=True, blank=True
    )
    banking_info = models.ForeignKey(
        PartnerBankingInfo, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.contact_person.name
