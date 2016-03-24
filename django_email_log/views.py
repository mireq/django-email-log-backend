# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import View

from .models import Email


class AttachmentView(View):
	def test_func(self):
		user = self.request.user
		return user.is_authenticated() and user.is_staff and user.has_perm('django_email_log.change_email')

	def get(self, request, **kwargs):
		if not self.test_func():
			return HttpResponseForbidden()
		email = get_object_or_404(Email, pk=kwargs['pk'])
		msg = email.parsed_message
		number = int(kwargs['nr']) - 1
		if kwargs['object_type'] == 'attachment':
			parts = msg['attachments']
		else:
			parts = msg['alternatives']
		if number >= len(parts):
			raise Http404()
		part = parts[number]
		content_type = part.get_content_type()
		if part.get_content_charset():
			content_type += '; charset=' + part.get_content_charset()

		response = HttpResponse(part.get_payload(decode=True), content_type=content_type)
		if kwargs['object_type'] == 'attachment':
			response['Content-Disposition'] = 'attachment; filename="%s"' % part.get_filename()
		return response
