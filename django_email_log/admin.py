# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from .models import Email


class EmailAdmin(admin.ModelAdmin):
	list_display = ('subject', 'get_recipients', 'date_sent', 'success')
	list_filter = ('date_sent', 'success')
	search_fields = ('subject', 'email_to')
	readonly_fields = ('subject', 'body', 'email_from', 'email_to', 'message_data', 'date_sent', 'success')

	def get_recipients(self, obj):
		return Truncator(obj.email_to).chars(40, truncate="...")
	get_recipients.short_description = _("recipients")
	get_recipients.allow_tags = True
	get_recipients.admin_order_field = "email_from"


admin.site.register(Email, EmailAdmin)
