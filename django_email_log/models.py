# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import email

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class EmailManager(models.Manager):
	def create_from_message(self, message, commit=True):
		db_message = Email()
		db_message.subject = message.subject
		db_message.body = message.body
		msg = message.message()
		db_message.email_from = msg.get('From', '')
		db_message.email_to = msg.get('To', '')
		db_message.message_data = msg.as_string()
		if commit:
			db_message.save()
		return db_message


@python_2_unicode_compatible
class Email(models.Model):
	objects = EmailManager()

	subject = models.TextField(verbose_name=_("subject"))
	body = models.TextField(verbose_name=_("body"))
	email_from = models.TextField(verbose_name=_("sender"))
	email_to = models.TextField(verbose_name=_("recipients"))
	message_data = models.TextField(verbose_name=_("message data"))

	date_sent = models.DateTimeField(verbose_name=_("date sent"), editable=False, db_index=True)
	success = models.BooleanField(verbose_name=_("successfully sent"), default=False, db_index=True)

	def __str__(self):
		return self.subject

	class Meta:
		verbose_name = _("e-mail message")
		verbose_name_plural = _("e-mail messages")
		ordering = ('-date_sent',)

	def save(self, *args, **kwargs):
		if not self.id and not self.date_sent:
			self.date_sent = timezone.now()
		return super(Email, self).save(*args, **kwargs)

	@property
	def parsed_message(self):
		msg = email.message_from_string(self.message_data.encode('utf-8'))
		parts = {
			'body': None,
			'attachments': [],
			'alternatives': [],
			'alternatives_annotated': [],
			'headers': dict(msg),
		}
		for part in msg.walk():
			if part.get_content_maintype() == 'multipart':
				continue
			if 'attachment' in part.get('Content-Disposition', ''):
				parts['attachments'].append(part)
			else:
				if part.get_content_type() == 'text/plain' and parts['body'] is None:
					parts['body'] = part.get_payload(decode=True)
					setattr(part, 'is_body', True)
				parts['alternatives'].append(part)
		for part in parts['alternatives']:
			parts['alternatives_annotated'].append((part.get_content_type(), part))
		return parts

	@property
	def email_message(self):
		msg = self.parsed_message
		attachments = []
		alternatives = []
		headers = {}
		skip_headers = {
			'Subject', 'From', 'To', 'Bcc', 'Cc',
			'Reply-To', 'Date',
			'Message-ID', 'Content-Type', 'MIME-Version'
		}

		for part in msg['attachments']:
			attachments.append((part.get_filename(), part.get_payload(decode=True), part.get_content_type()))
		for part in msg['alternatives']:
			if not getattr(part, 'is_body', False):
				alternatives.append((part.get_payload(decode=True), part.get_content_type()))
		for hdr, value in msg['headers'].items():
			if hdr not in skip_headers:
				headers[hdr] = value

		email_instance = EmailMultiAlternatives(
			subject=msg['headers']['Subject'],
			body=msg['body'] or '',
			from_email=msg['headers'].get('From'),
			to=msg['headers']['To'].split(', ') if 'To' in msg['headers'] else None,
			bcc=msg['headers']['Bcc'].split(', ') if 'Bcc' in msg['headers'] else None,
			cc=msg['headers']['Cc'].split(', ') if 'Cc' in msg['headers'] else None,
			reply_to=msg['headers']['Reply-To'].split(', ') if 'Reply-To' in msg['headers'] else None,
			attachments=attachments or None,
			alternatives=alternatives or None,
			headers=headers or None,
		)
		setattr(email_instance, 'model_instance', self)

		return email_instance
