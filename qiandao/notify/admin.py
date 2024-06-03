from django.contrib import admin

from .models import (
    BarkNotification,
    ServerChanNotification,
    PushDeerNotification
)


# admin.site.register(ServerChanNotification)


@admin.register(BarkNotification)
class BarkNotificationAdmin(admin.ModelAdmin):
    list_display = ["name", "server", "device_id", "enable"]
    list_filter = ["enable"]


@admin.register(PushDeerNotification)
class PushDeerNotificationAdmin(admin.ModelAdmin):
    list_display = ["name", "server", "push_key", "enable"]
    list_filter = ["enable"]
