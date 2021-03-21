# -*- coding: utf-8 -*-
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.urls import re_path

from .views import AttachmentView


urlpatterns = [
	re_path(r'^parts/(?P<object_type>(attachment|alternative))/(?P<pk>\d+)/(?:(?P<nr>\d+)/)?', xframe_options_sameorigin(AttachmentView.as_view()), name='django_email_log_attachment'),
]
