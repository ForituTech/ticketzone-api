from django.contrib import admin

from .models import Partner, PartnerBankingInfo, Person

admin.site.register([Person, PartnerBankingInfo, Partner])
