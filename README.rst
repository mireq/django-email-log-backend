============================
Django database email logger
============================

Install
-------

`pip install https://github.com/mireq/django-email-log-backend.git`

Usage
-----

Settings
^^^^^^^^

.. code:: python

	INSTALLED_APPS = (
		# ...
		'django_email_log',
	)

	EMAIL_BACKEND = 'django_email_log.backends.EmailBackend'
	EMAIL_LOG_BACKEND = 'django.core.mail.backends.console.EmailBackend'

Emails are forwarded to `EMAIL_LOG_BACKEND`.

.. code:: python

	# urls.py
	urlpatterns = patterns('',
		# ...
		url(r'^django-email-log/', include('django_email_log.urls')),
	)

.. image:: https://raw.github.com/wiki/mireq/django-email-log-backend/msg1.png

.. image:: https://raw.github.com/wiki/mireq/django-email-log-backend/msg2.png
