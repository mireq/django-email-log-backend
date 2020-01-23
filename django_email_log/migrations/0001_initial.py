# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-20 14:08
from django.db import migrations, models


class Migration(migrations.Migration):

	initial = True

	dependencies = [
	]

	operations = [
		migrations.CreateModel(
			name='Email',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('subject', models.TextField(verbose_name='subject')),
				('body', models.TextField(verbose_name='body')),
				('email_from', models.TextField(verbose_name='sender')),
				('email_to', models.TextField(verbose_name='recipients')),
				('message_data', models.TextField(verbose_name='message data')),
				('date_sent', models.DateTimeField(db_index=True, editable=False, verbose_name='date sent')),
				('success', models.BooleanField(db_index=True, default=False, verbose_name='successfully sent')),
			],
			options={
				'ordering': ('-date_sent',),
				'verbose_name': 'e-mail message',
				'verbose_name_plural': 'e-mail messages',
			},
		),
	]
