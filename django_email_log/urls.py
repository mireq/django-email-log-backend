# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from .views import AttachmentView


urlpatterns = [
	url(r'^parts/(?P<object_type>(attachment|alternative))/(?P<pk>\d+)/(?P<nr>\d+)/', AttachmentView.as_view(), name='django_email_log_attachment'),
]
