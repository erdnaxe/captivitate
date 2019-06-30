# -*- mode: python; coding: utf-8 -*-
# Copyright (C) 2016-2019 by Cr@ns
# SPDX-License-Identifier: GPL-2.0-or-later
# This file is part of captivitate.

import re
import sys

from setuptools import find_packages, setup


# Calculate the version number without importing the postorius package.
with open('src/captivitate/__init__.py') as fp:
    for line in fp:
        mo = re.match("__version__ = '(?P<version>[^']+?)'", line)
        if mo:
            __version__ = mo.group('version')
            break
    else:
        print('No version number found')
        sys.exit(1)


setup(
    name="captivitate",
    version=__version__,
    description="A captive portal for guest networks",
    long_description=open('README.md').read(),
    maintainer="Cr@ns",
    license='GPLv2',
    keywords='ipset iptables captive portal django',
    url="https://github.com/erdnaxe/captivitate",
    classifiers=[
        "Framework :: Django",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'Django>=1.11,<2.3',
        'django-bootstrap3>=11.0',
        'django-macaddress>=1.5',
        'django-reversion>=2.0.8',
        'django-prometheus>=1.0.6',
        'django-crans-theme>=0.1.0',
    ],
    tests_require=[],
)
