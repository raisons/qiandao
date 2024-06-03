#!/usr/bin/env python


from django.contrib import admin


class AdminSite(admin.AdminSite):
    site_title = "每日签到"
    site_header = "每日签到管理系统"
    index_title = "每日签到"


site = AdminSite()
