from django.contrib import admin

from .models import (
    Partner,
    PartnerBankingInfo,
    PartnerPerson,
    PartnerPromotion,
    PartnerSMS,
    Person,
)

admin.site.register(
    [Person, PartnerBankingInfo, Partner, PartnerPerson, PartnerSMS, PartnerPromotion]
)
