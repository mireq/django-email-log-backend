# -*- coding: utf-8 -*-
from distutils.cmd import Command
from distutils.command.build import build as _build

import setuptools
from setuptools.command.install_lib import install_lib as _install_lib
from setuptools.command.develop import develop as _develop


class compile_translations(Command):
	description = 'Compiles translations"'
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		import os

		if 'DJANGO_SETTINGS_MODULE' in os.environ:
			del os.environ['DJANGO_SETTINGS_MODULE']

		from django.core.management import call_command

		curdir = os.getcwd()
		call_command('compilemessages')
		os.chdir(curdir)


class build(_build):
	sub_commands = [('compile_translations', None)] + _build.sub_commands


class install_lib(_install_lib):
	def run(self):
		self.run_command('compile_translations')
		_install_lib.run(self)


class develop(_develop):
	def run(self):
		self.run_command('compile_translations')
		_develop.run(self)


with open('README.rst', 'r') as fh:
	long_description = fh.read()


setuptools.setup(
	name='django-email-log-backend',
	version='0.3',
	author='Miroslav Bendík',
	author_email='miroslav.bendik@gmail.com',
	description="Django email log backend",
	long_description=long_description,
	long_description_content_type='text/x-rst',
	url='https://github.com/mireq/django-email-log-backend',
	packages=setuptools.find_packages(),
	include_package_data=True,
	python_requires='>=3',
	setup_requires=['django'],
	cmdclass={'build': build, 'install_lib': install_lib, 'develop': develop, 'compile_translations': compile_translations},
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
)
