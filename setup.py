#!/usr/bin/env python
"""
sentry-auth-gitlab
==================

:copyright: (c) 2015 Functional Software, Inc
"""
from __future__ import absolute_import
from setuptools import setup, find_packages


tests_require = [
    'pytest',
    'mock',
]

install_requires = [
    'sentry',
]

setup(
    name='sentry-auth-gitlab',
    version='0.1.0',
    author='Sky Lothar',
    author_email='allothar@gmail.com@gmail.com',
    url='https://github.com/skylothar',
    description='Gitlab authentication provider for Sentry',
    long_description=__doc__,
    license='',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'tests': tests_require},
    include_package_data=True,
    package_data={
        "auth_gitlab": [
            "templates/sentry_auth_gitlab/*.html",
        ],
    },
    entry_points={
        'sentry.apps': [
            'auth_gitlab = auth_gitlab.apps.Config',
         ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
