# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in monschool/__init__.py
from mon_school import __version__ as version

setup(
	name='mon_school',
	version=version,
	description='Frappe App for Mon School branding',
	author='FOSS United',
	author_email='anand@fossunited.org',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
