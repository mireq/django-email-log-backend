# -*- coding: utf-8 -*-
from django.apps import AppConfig as CoreAppConfig
from django.core import checks
from django.utils.translation import gettext_lazy as _

from .checks import check_settings


class AppConfig(CoreAppConfig):
	name = 'django_email_log'
	verbose_name = _("Email log")

	def ready(self):
		checks.register()(check_settings)
