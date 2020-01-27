# -*- coding: utf-8 -*-
import email

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _


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
		msg = email.message_from_string(force_str(self.message_data))
		parts = {
			'body': None,
			'attachments': [],
			'attachments_annotated': [],
			'alternatives': [],
			'alternatives_annotated': [],
			'parts': [],
			'parts_cid': {},
			'headers': dict(msg),
		}
		if msg.is_multipart():
			for i, part in enumerate(msg.get_payload()):
				attachments, alternatives = self.__decode_part(part)
				if i == 0:
					parts['alternatives'] += attachments
					parts['alternatives'] += alternatives
				else:
					parts['attachments'] += attachments
					parts['alternatives'] += alternatives
		else:
			attachments, alternatives = self.__decode_part(msg)
			parts['attachments'] += attachments
			parts['alternatives'] += alternatives

		for part in parts['attachments']:
			parts['attachments_annotated'].append((part.get_content_type(), part))
		for part in parts['alternatives']:
			parts['alternatives_annotated'].append((part.get_content_type(), part))
		for i, part in enumerate(msg.walk()):
			parts['parts'].append(part)
			kwargs = {'pk': self.pk, 'nr': i}
			kwargs['object_type'] = 'attachment'
			part['attachment_url'] = reverse('django_email_log_attachment', kwargs=kwargs)
			kwargs['object_type'] = 'alternative'
			part['alternative_url'] = reverse('django_email_log_attachment', kwargs=kwargs)
			cid = part.get('Content-ID')
			if cid:
				if cid.startswith('<') and cid.endswith('>'):
					cid = cid[1:-1]
				parts['parts_cid'][cid] = part

		body = dict(parts['alternatives_annotated']).get('text/plain')
		if body:
			parts['body'] = part.get_payload(decode=True)
			setattr(part, 'is_body', True)
		return parts

	def __decode_part(self, part):
		attachments = []
		alternatives = []
		if part.is_multipart():
			for payload in part.get_payload():
				if 'attachment' in payload.get('Content-Disposition', ''):
					attachments.append(payload)
				else:
					alternatives.append(payload)

		else:
			if 'attachment' in part.get('Content-Disposition', ''):
				attachments.append(part)
			else:
				alternatives.append(part)
		return attachments, alternatives

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
