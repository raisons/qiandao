from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from system import models

admin.site.register(models.Proxies)
admin.site.register(models.User, UserAdmin)


admin.site.unregister(Group)

