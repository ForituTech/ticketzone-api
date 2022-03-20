from django.contrib import admin

from notifications.models import Notification
from notifications.utils import resend_notification


class NotificationsAdminConfig(admin.ModelAdmin):
    search_fields = ["person__name", "message"]
    actions = [resend_notification]
    readonly_fields = ["sent", "has_data"]


admin.site.register(Notification, NotificationsAdminConfig)
