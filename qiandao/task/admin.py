from django.contrib import admin
from task.models import (
    V2ex,
    Tank,
    MLoL,
    ItHome,
    LinuxDo,
    Alipan,
)


@admin.register(ItHome)
class ItHomeAdmin(admin.ModelAdmin):
    list_display = ("name", "username", "password", "enable")
    list_filter = ("enable",)


@admin.register(V2ex)
class V2exAdmin(admin.ModelAdmin):
    list_display = ("name", "short_cookies", "enable")


@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "device_id",
        "short_refresh_token",
        "short_access_token",
        "enable"
    )
    list_filter = ("enable",)


@admin.register(MLoL)
class MLoLAdmin(admin.ModelAdmin):
    list_display = ("name", "client_ticket", "user_id", "enable")


@admin.register(LinuxDo)
class LinuxDoAdmin(admin.ModelAdmin):
    list_display = ("name", "short_cookies", "csrf_token", "username", "enable")


@admin.register(Alipan)
class AlipanAdmin(admin.ModelAdmin):
    list_display = ("name", "refresh_token", "enable")
