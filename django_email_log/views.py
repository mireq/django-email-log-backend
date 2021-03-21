# -*- coding: utf-8 -*-
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
		msg = email.parsed_message
		number = int(kwargs.get('nr', '0'))
		if number > len(msg['parts']):
			raise Http404()
		part = msg['parts'][number]
		content_type = part.get_content_type()
		if part.get_content_charset():
			content_type += '; charset=' + part.get_content_charset()

		part_data = part.get_payload(decode=True)
		charset = part.get_content_charset('iso-8859-1' if part.get_content_maintype() == 'text' else None)
		if charset == 'utf-8':
			part_data = part_data.decode('raw-unicode-escape')
		else:
			if charset:
				part_data = part_data.decode(charset, 'replace')
		if part.get_content_type() == 'text/html':
			for cid, part in msg['parts_cid'].items():
				part_data = part_data.replace('cid:' + cid, part['alternative_url'])
		response = HttpResponse(part_data, content_type=content_type)
		if kwargs['object_type'] == 'attachment':
			response['Content-Disposition'] = 'attachment; filename="%s"' % part.get_filename()
		return response
