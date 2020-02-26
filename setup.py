# -*- coding: utf-8 -*-
"""Installer for the eionet.theme package."""

import os

from setuptools import find_packages, setup

NAME = 'eionet.theme'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(
    name=NAME,
    version=VERSION,
    description="Installable theme: eionet.theme",
    long_description_content_type="text/x-rst",
    long_description=open("README.rst").read() + "\n" +
    open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Krisztina Elekes',
    author_email='krisztina.elekes@eaudeweb.ro',
    url='https://github.com/eea/eionet.plone.theme',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['eionet'],
    # package_dir={'': ''},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'Products.GenericSetup>=1.8.2',
        'setuptools',
        'z3c.jbot',
        'plone.app.theming',
        'plone.app.themingplugins',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
