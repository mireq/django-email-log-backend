# -*- coding: utf-8 -*-
import logging

import celery

from ..backends import current_message
from ..models import Email


logger = logging.getLogger(__name__)


class DjceleryEmailTask(celery.Task):
	"""
	E-mail celery task instance with status capturing.
	"""

	def after_return(self, status, retval, task_id, args, kwargs, einfo):
		if status in ('SUCCESS', 'FAILURE', 'REVOKED') and 'email_id' in kwargs:
			try:
				success = (status == 'SUCCESS' and int(retval) > 0)
				email_status = Email.STATUS_SUCCESS if success else Email.STATUS_FAIL
			except Exception:
				email_status = Email.STATUS_FAIL
			Email.objects.filter(pk=kwargs['email_id']).update(status=email_status)

	def delay(self, *args, **kwargs):
		email_id = current_message.get().pk
		kwargs['email_id'] = email_id
		return super().delay(*args, **kwargs)


def djcelery_email_handler(status, email):
	"""
	Handles e-mail status if backend directly returns number of sent messages or
	do nothing if returns AsyncResult.
	"""
	try:
		sent = int(status or 0)
		email.status = Email.STATUS_SUCCESS if sent > 0 else Email.STATUS_FAIL
		return sent
	except Exception:
		return 0
