# -*- coding: utf-8 -*-

from __future__ import print_function

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import os
import sys
import codecs

import cronls

# -------------------------------------------------------------------- #

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    """Return multiple read calls to different readable objects as a single
    string."""
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(HERE, *parts), 'r').read()

LONG_DESCRIPTION = read('README.md')

# -------------------------------------------------------------------- #

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--strict',
            '--verbose',
            '--tb=long',
            'cronls/test']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

# -------------------------------------------------------------------- #

setup(
	name='cronls',
	version=cronls.__version__,
	url='https://github.com/caiok/cronls/',
	license='The MIT License (MIT)',
	author='Francesco Caliumi',
	tests_require=['pytest', 'pytest-cov'],
	install_requires=[

	],
	scripts=[
		'cronls/cronls.py'
	],
	cmdclass={
		'test': PyTest
	},
	entry_points={
		'console_scripts': [
			'cronls = cronls.cronls:CronlsCommand'
		]
	},
	author_email='francesco.caliumi@gmail.com',
	description='Automated REST APIs for existing database-driven systems',
	long_description=LONG_DESCRIPTION,
	packages=['cronls'],
	include_package_data=True,
	platforms='any',
	test_suite='cronls.test',
	zip_safe=False,
	classifiers = [
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
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
		'testing': ['pytest', 'pytest-cov'],
	}
)