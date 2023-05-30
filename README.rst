============================
Django database email logger
============================

Install
-------

.. code:: bash

	pip install django-email-log-backend

or

.. code:: bash

	pip install -e 'git+https://github.com/mireq/django-email-log-backend.git#egg=django_email_log_backend'

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
	urlpatterns = [
		# ...
		path('django-email-log/', include('django_email_log.urls')),
	]

Screenshots
^^^^^^^^^^^

.. image:: https://raw.github.com/wiki/mireq/django-email-log-backend/msg1.png?v2020-04-03

.. image:: https://raw.github.com/wiki/mireq/django-email-log-backend/msg2.png?v2020-04-03

.. image:: https://raw.github.com/wiki/mireq/django-email-log-backend/msg3.png?v2020-04-03
