# -*- coding: utf-8 -*-
import logging
from contextvars import ContextVar as cv

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend
from django.utils import timezone
from django.utils.module_loading import import_string

from .models import Email
from .utils import get_status_handler


logger = logging.getLogger(__name__)
current_message = cv('current_email_message_instance')


class EmailBackend(BaseEmailBackend):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.connection = get_connection(settings.EMAIL_LOG_BACKEND, **kwargs)
		handler = get_status_handler()
		self.process_status = import_string(handler)

	def send_messages(self, email_messages):
		num_sent = 0
		for message in email_messages:
			message.connection = self.connection
			email = self.get_email_instance(message)
			current_message.set(email)
			try:
				num_sent += self.process_status(message.send(), email)
			except Exception:
				logger.exception("Wrong e-mail status value", extra={'value': num_sent})
			email.save()
		return num_sent

	def get_email_instance(self, message):
		if hasattr(message, 'model_instance'):
			model_instance = message.model_instance
		else:
			try:
				model_instance = Email.objects.create_from_message(message)
			except Exception:
				extra = {'email': message}
				logger.exception("E-mail message not serialized", extra=extra)
				model_instance = Email(
					subject='<error>',
					date_sent=timezone.now(),
					status=Email.STATUS_FAIL
				)
		model_instance.original_message = message
		return model_instance
