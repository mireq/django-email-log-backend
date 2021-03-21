# -*- coding: utf-8 -*-
from collections import namedtuple
import cgi
import email

from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import pgettext_lazy


PartInfo = namedtuple('PartInfo', ['part', 'content_type', 'content_disposition', 'filename', 'cid', 'absolute_url', 'alternative_url'])


class EmailRawMessage(EmailMultiAlternatives):
	def __init__(self, raw, *args, **kwargs):
		self.__raw = raw
		super().__init__(*args, **kwargs)

	def _create_message(self, msg): # pylint: disable=unused-argument
		return self.__raw

	def message(self):
		return self._create_message(None)


class EmailManager(models.Manager):
	def create_from_message(self, message, commit=True):
		db_message = Email()
		db_message.subject = message.subject
		db_message.body = message.body
		msg = message.message()
		db_message.email_from = msg.get('From', '')
		db_message.email_to = msg.get('To', '')
		db_message.message_data = msg.as_bytes()
		if commit:
			db_message.save()
		return db_message


class Email(models.Model):
	objects = EmailManager()

	STATUS_PENDING = 'p'
	STATUS_SUCCESS = 's'
	STATUS_FAIL = 'f'
	STATUS_RECEIVED = 'r'
	STATUS_CHOICES = (
		(STATUS_PENDING, pgettext_lazy('email message status', "Pending")),
		(STATUS_SUCCESS, pgettext_lazy('email message status', "Success")),
		(STATUS_FAIL, pgettext_lazy('email message status', "Fail")),
		(STATUS_RECEIVED, pgettext_lazy('email message status', "Received")),
	)

	subject = models.TextField(verbose_name=pgettext_lazy('email message', "subject"))
	body = models.TextField(verbose_name=pgettext_lazy('email message', "body"))
	email_from = models.TextField(verbose_name=pgettext_lazy('email message', "sender"))
	email_to = models.TextField(verbose_name=pgettext_lazy('email message', "recipients"))
	message_data = models.BinaryField(verbose_name=pgettext_lazy('email message', "data"))

	date_sent = models.DateTimeField(verbose_name=pgettext_lazy('email message', "date sent"), editable=False, db_index=True)
	status = models.CharField(verbose_name=pgettext_lazy('email message', "status"), max_length=1, default=STATUS_PENDING, choices=STATUS_CHOICES, db_index=True)
	readed = models.BooleanField(verbose_name=pgettext_lazy('email message', "readed"), blank=True, default=False, db_index=True)

	def __str__(self):
		return self.subject

	class Meta:
		verbose_name = pgettext_lazy('email message noun', "e-mail message")
		verbose_name_plural = pgettext_lazy('email message noun plural', "e-mail messages")
		ordering = ('-date_sent',)

	def save(self, *args, **kwargs):
		if not self.id and not self.date_sent:
			self.date_sent = timezone.now()
		return super().save(*args, **kwargs)

	@property
	def parsed_message(self):
		return email.message_from_bytes(self.message_data.tobytes())

	@property
	def payload_tree(self):
		return self.__preprocessed_message['tree']

	@property
	def payload_list(self):
		return self.__preprocessed_message['parts']

	@property
	def alternatives(self):
		return self.__preprocessed_message['alternatives']

	@property
	def __preprocessed_message(self):
		state = {'tree': {}, 'parts': [], 'alternatives': []}
		self.__build_tree(self.parsed_message, state['tree'], state, add_to_alternative=True)
		return state

	def __build_tree(self, part, tree, state, add_to_alternative):
		parts, alternatives = state['parts'], state['alternatives']
		content_disposition, params = cgi.parse_header(part.get('Content-Disposition', ''))
		filename = params.get('filename')
		content_disposition = content_disposition or 'inline'
		content_type = part.get_content_type()
		cid = part.get('Content-ID')
		if cid:
			if cid.startswith('<') and cid.endswith('>'):
				cid = cid[1:-1]
		tree['filename'] = filename
		tree['content_type'] = content_type
		tree['content_disposition'] = content_disposition
		tree['index'] = len(parts)
		tree['cid'] = len(parts)
		tree['absolute_url'] = reverse('django_email_log_attachment', args=('attachment', self.pk, tree['index']))
		tree['alternative_url'] = reverse('django_email_log_attachment', args=('alternative', self.pk, tree['index']))
		part_info = PartInfo(part, content_type, content_disposition, filename, cid, tree['absolute_url'], tree['alternative_url'])
		parts.append(part_info)
		if part.is_multipart():
			tree['children'] = []
			add_to_alternative = len(alternatives) == 0
			for payload in part.get_payload():
				subtree = {}
				tree['children'].append(subtree)
				self.__build_tree(payload, subtree, state, add_to_alternative)
		else:
			if add_to_alternative and part_info.content_disposition == 'inline':
				alternatives.append(part_info)
			tree['payload'] = part.get_payload()
		return part_info

	@property
	def email_message(self):
		msg = self.parsed_message
		email_instance = EmailRawMessage(
			raw=msg,
			from_email=msg.get('From'),
			to=msg['To'].split(', ') if 'To' in msg else None
		)
		setattr(email_instance, 'model_instance', self)
		return email_instance
