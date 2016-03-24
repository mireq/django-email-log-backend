# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from .models import Email


class EmailBackend(BaseEmailBackend):
	def __init__(self, **kwargs):
		super(EmailBackend, self).__init__(**kwargs)
		self.connection = get_connection(settings.EMAIL_LOG_BACKEND, **kwargs)

	def send_messages(self, email_messages):
		num_sent = 0
		for message in email_messages:
			message.connection = self.connection
			if hasattr(message, 'model_instance'):
				sent = message.send()
				num_sent += sent
				if sent > 0:
					message.model_instance.success = True
					message.model_instance.save()
			else:
				email = Email.objects.create_from_message(message)
				sent = message.send()
				num_sent += sent
				if sent > 0:
					email.success = True
					email.save()
		return num_sent
