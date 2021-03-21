# -*- coding: utf-8 -*-
import mimetypes
import os

from django.http.response import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import View

from .models import Email


class AttachmentView(View):
	def test_func(self):
		user = self.request.user
		return user.is_authenticated and user.is_staff and user.has_perm('django_email_log.change_email')

	def get(self, request, **kwargs):
		if not self.test_func():
			return HttpResponseForbidden()
		email = get_object_or_404(Email, pk=kwargs['pk'])
		payloads = email.payload_list
		number = int(kwargs.get('nr', '0'))
		if number > len(payloads):
			raise Http404()
		payload = payloads[number]
		part = payload.part
		content_type = part.get_content_type()
		if part.get_content_charset():
			content_type += '; charset=' + part.get_content_charset()

		if not 'nr' in kwargs:
			part_data = email.message_data
			content_type = 'text/plain; charset=utf-8'
		elif part.is_multipart():
			part_data = part.as_string()
			content_type = 'text/plain'
		else:
			part_data = part.get_payload(decode=True)
			charset = part.get_content_charset('iso-8859-1' if part.get_content_maintype() == 'text' else None)
			if charset == 'utf-8':
				try:
					part_data = part_data.decode('utf-8')
				except UnicodeDecodeError:
					part_data = part_data.decode('raw-unicode-escape')
			else:
				if charset:
					part_data = part_data.decode(charset, 'replace')
			if part.get_content_type() == 'text/html':
				for part in payloads:
					if part.cid:
						part_data = part_data.replace('cid:' + part.cid, part['get_absolute_url'])
		response = HttpResponse(part_data, content_type=content_type)
		if kwargs['object_type'] == 'attachment':
			ext = mimetypes.guess_extension(payload.content_type, strict=True)
			filename = payload.filename
			if filename is None:
				filename = email.date_sent.strftime('%Y-%m-%d_%H-%M-%S')
				filename = "%s_%d_%d" % (filename, email.pk, number)
			if ext:
				filename, __ = os.path.splitext(filename)
				filename = filename + ext
			response['Content-Disposition'] = 'attachment; filename="%s"' % filename.replace('"', '')
		return response
