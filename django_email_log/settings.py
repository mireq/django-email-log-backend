# -*- coding: utf-8 -*-
from django.conf import settings


EMAIL_LOG_BACKEND = getattr(settings, "EMAIL_LOG_BACKEND", 'django.core.mail.backends.console.EmailBackend')
EMAIL_LOG_STATUS_HANDLER = getattr(settings, "EMAIL_LOG_STATUS_HANDLER", None)
EMAIL_LOG_STATUS_HANDLER_MAP = getattr(settings, "EMAIL_LOG_STATUS_HANDLER_MAP", {
	'': 'email_log_bacend.status_handlers.base.handler',
})
