# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from .models import Email


class EmailBackend(BaseEmailBackend):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.connection = get_connection(settings.EMAIL_LOG_BACKEND, **kwargs)

	def send_messages(self, email_messages):
		num_sent = 0
		for message in email_messages:
			message.connection = self.connection
			if hasattr(message, 'model_instance'):
				sent = message.send() or 0
				num_sent += sent
				message.model_instance.status = Email.STATUS_SUCCESS if sent > 0 else Email.STATUS_FAIL
				message.model_instance.save()

			else:
				email = Email.objects.create_from_message(message)
				sent = message.send() or 0
				try:
					num_sent += sent
				except Exception:
					sent = 0
				message.model_instance.status = Email.STATUS_SUCCESS if sent > 0 else Email.STATUS_FAIL
				email.save()
		return num_sent
