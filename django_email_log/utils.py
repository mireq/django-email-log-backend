# -*- coding: utf-8 -*-
from django.conf import settings


EMAIL_LOG_STATUS_HANDLER_MAP = getattr(settings, 'EMAIL_LOG_STATUS_HANDLER_MAP', {
	'': 'django_email_log.status_handlers.base.handler',
	'djcelery_email.backends.CeleryEmailBackend': 'django_email_log.status_handlers.celery.djcelery_email_handler'
})


def get_status_handler():
	handler = getattr(settings, 'EMAIL_LOG_STATUS_HANDLER', None)
	if handler is None:
		handler = EMAIL_LOG_STATUS_HANDLER_MAP.get(settings.EMAIL_LOG_BACKEND, EMAIL_LOG_STATUS_HANDLER_MAP[''])
	return handler
