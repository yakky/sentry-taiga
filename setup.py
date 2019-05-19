#!/usr/bin/env python
"""
sentry-taiga
=============

An extension for Sentry which integrates with Taiga. Specifically, it allows
you to easily create issues from events within Sentry.

:copyright: (c) 2015 RochSystems LLC, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""
from setuptools import setup, find_packages


tests_require = [
    'nose',
]

install_requires = [
    'sentry>=5.0.0',
    'python-taiga==0.9',
]

setup(
    name='sentry-taiga',
    version=open('VERSION').read().strip(),
    author='Sentry',
    author_email='hello@sentry.io',
    url='http://github.com/getsentry/sentry-taiga',
    description='A Sentry extension which integrates with Taiga.',
    long_description=__doc__,
    license='MIT',
    packages=find_packages(),
    zip_safe=True,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'taiga = sentry_taiga',
        ],
        'sentry.plugins': [
            'taiga = sentry_taiga.plugin:TaigaPlugin'
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
