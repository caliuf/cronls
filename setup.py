from __future__ import print_function

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import os
import sys

import cronls

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
	encoding = kwargs.get('encoding', 'utf-8')
	sep = kwargs.get('sep', '\n')
	buf = []
	for filename in filenames:
		with io.open(filename, encoding=encoding) as f:
			buf.append(f.read())
	return sep.join(buf)

long_description = read('README.md', 'CHANGES.md')

class PyTest(TestCommand):
	def finalize_options(self):
		TestCommand.finalize_options(self)
		self.test_args = []
		self.test_suite = True

	def run_tests(self):
		import pytest
		errcode = pytest.main(self.test_args)
		sys.exit(errcode)

setup(
	name='cronls',
	version=cronls.__version__,
	url='https://github.com/caiok/cronls/',
	license='The MIT License (MIT)',
	author='Francesco Caliumi',
	tests_require=['pytest'],
	install_requires=[
		
	],
	scripts=[
		'cronls/cronls.py'
	],
	cmdclass={
		'test': PyTest
	},
	author_email='francesco.caliumi@gmail.com',
	description='Automated REST APIs for existing database-driven systems',
	long_description=long_description,
	packages=['cronls'],
	include_package_data=True,
	platforms='any',
	test_suite='cronls.test.test_cronls',
	classifiers = [
		'Programming Language :: Python',
		'Development Status :: 5 - Production/Stable',
		'Natural Language :: English',
		'Environment :: Console',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: MIT License',
		'Operating System :: POSIX :: Linux',
		'Topic :: System :: Systems Administration',
		'Topic :: Utilities',
	],
	extras_require={
		'testing': ['pytest'],
	}
)