# -*- coding: utf-8 -*-
from django.apps import AppConfig as CoreAppConfig
from django.utils.translation import gettext_lazy as _


class AppConfig(CoreAppConfig):
	name = 'django_email_log'
	verbose_name = _("Email log")
