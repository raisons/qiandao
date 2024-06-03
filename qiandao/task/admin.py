from django.contrib import admin
from django.utils.html import format_html
from task.models import (
    V2ex,
    Tank,
    MLoL,
    ItHome,
    LinuxDo
)


class CookiesMixin:
    cookies_max_length: int = 50

    @admin.display(description="Cookies")
    def short_cookies(self, obj):
        max_length = 50
        if len(obj.cookies) > max_length:
            return format_html(
                '<span>{} ...</span>',
                obj.cookies[:max_length]
            )
        return obj.description


@admin.register(ItHome)
class ItHomeAdmin(admin.ModelAdmin):
    list_display = ("name", "username", "password", "enable")
    list_filter = ("enable",)


@admin.register(V2ex)
class V2exAdmin(admin.ModelAdmin, CookiesMixin):
    list_display = ("name", "short_cookies", "enable")


@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = ("name", "access_token", "enable")
    list_filter = ("enable",)


@admin.register(MLoL)
class MLoLAdmin(admin.ModelAdmin):
    list_display = ("name", "client_ticket", "user_id", "enable")


@admin.register(LinuxDo)
class LinuxDoAdmin(admin.ModelAdmin, CookiesMixin):
    list_display = ("name", "short_cookies", "csrf_token", "username", "enable")
