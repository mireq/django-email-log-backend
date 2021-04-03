# -*- coding: utf-8 -*-
import logging

from ..models import Email


logger = logging.getLogger(__name__)


def handler(status, email):
	try:
		sent = int(status or 0)
	except Exception:
		extra = {
			'status': status,
			'email': email.original_message,
			'instance': email,
		}
		logger.exception("E-mail backend has returned invalid status", extra=extra)
		sent = 0
	email.status = Email.STATUS_SUCCESS if sent > 0 else Email.STATUS_FAIL
	return sent
