# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from .models import Email


class EmailAdmin(admin.ModelAdmin):
	list_display = ('subject', 'get_recipients', 'date_sent', 'status')
	list_filter = ('date_sent', 'status', 'readed')
	search_fields = ('subject', 'email_to')
	readonly_fields = ('body', 'email_from', 'email_to', 'message_data', 'date_sent', 'status', 'readed')
	fields = ('email_from', 'email_to', 'date_sent', 'status')

	def get_recipients(self, obj):
		return Truncator(obj.email_to).chars(40, truncate="...")
	get_recipients.short_description = _("recipients")
	get_recipients.allow_tags = True
	get_recipients.admin_order_field = "email_from"

	def has_add_permission(self, request): # pylint: disable=unused-argument
		return False

	def change_view(self, request, object_id, *args, **kwargs):
		message = self.get_object(request, unquote(object_id))
		if not message.readed:
			message.readed = True
			message.save(update_fields=['readed'])
		return super().change_view(request, object_id, *args, **kwargs)


admin.site.register(Email, EmailAdmin)
