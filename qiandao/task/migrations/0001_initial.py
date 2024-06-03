# Generated by Django 5.0.6 on 2024-06-01 13:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItHome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='名称')),
                ('enable', models.BooleanField(default=False, verbose_name='启用')),
                ('username', models.CharField(max_length=64, verbose_name='用户名')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
                ('proxy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.proxies', verbose_name='代理')),
            ],
            options={
                'verbose_name': 'IT之家配置',
                'verbose_name_plural': 'IT之家',
            },
        ),
        migrations.CreateModel(
            name='LinuxDo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='名称')),
                ('enable', models.BooleanField(default=False, verbose_name='启用')),
                ('cookies', models.TextField()),
                ('csrf_token', models.TextField()),
                ('username', models.CharField(blank=True, max_length=32, null=True)),
                ('proxy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.proxies', verbose_name='代理')),
            ],
            options={
                'verbose_name': 'Linux.do配置',
                'verbose_name_plural': 'Linux.do',
            },
        ),
        migrations.CreateModel(
            name='MLoL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='名称')),
                ('enable', models.BooleanField(default=False, verbose_name='启用')),
                ('client_ticket', models.TextField()),
                ('user_id', models.CharField(max_length=128)),
                ('proxy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.proxies', verbose_name='代理')),
            ],
            options={
                'verbose_name': '掌上英雄联盟配置',
                'verbose_name_plural': '掌上英雄联盟',
            },
        ),
        migrations.CreateModel(
            name='Tank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='名称')),
                ('enable', models.BooleanField(default=False, verbose_name='启用')),
                ('access_token', models.TextField()),
                ('proxy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.proxies', verbose_name='代理')),
            ],
            options={
                'verbose_name': '坦克App配置',
                'verbose_name_plural': '坦克App',
            },
        ),
        migrations.CreateModel(
            name='V2ex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='名称')),
                ('enable', models.BooleanField(default=False, verbose_name='启用')),
                ('cookies', models.TextField()),
                ('proxy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='system.proxies', verbose_name='代理')),
            ],
            options={
                'verbose_name': 'V2EX配置',
                'verbose_name_plural': 'V2EX',
            },
        ),
    ]