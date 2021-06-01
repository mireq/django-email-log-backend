import django

if not django.VERSION >= (3, 2):
	default_app_config = 'django_email_log.apps.AppConfig'
