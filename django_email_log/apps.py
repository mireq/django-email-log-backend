# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig as CoreAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(CoreAppConfig):
	name = 'django_email_log'
	verbose_name = _("Email log")
