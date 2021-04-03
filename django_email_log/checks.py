# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.checks import Warning # pylint: disable=redefined-builtin
from django.utils.module_loading import import_string

from .utils import get_status_handler


def check_settings(**kwargs):
	issues = []

	status_handler = get_status_handler()

	if status_handler == 'django_email_log.status_handlers.celery.djcelery_email_handler':
		from .status_handlers.celery import DjceleryEmailTask
		config = getattr(settings, 'CELERY_EMAIL_TASK_CONFIG', None)

		if config is None:
			return [Warning(
				"Missing CELERY_EMAIL_TASK_CONFIG settings",
				hint="Add CELERY_EMAIL_TASK_CONFIG to settings",
				id='django_email_log.W001'
			)]
		if not 'base' in config:
			return [Warning(
				"Base attribute not in CELERY_EMAIL_TASK_CONFIG",
				hint="Add 'base': 'django_email_log.status_handlers.celery.DjceleryEmailTask' to CELERY_EMAIL_TASK_CONFIG",
				id='django_email_log.W002'
			)]
		base_name = str(config['base'])
		base = config['base']
		if isinstance(base, str):
			base = import_string(base)
		if not issubclass(base, DjceleryEmailTask):
			return [Warning(
				"%s is not subclass of django_email_log.status_handlers.celery.DjceleryEmailTask" % base_name,
				id='django_email_log.W003'
			)]
	return issues
