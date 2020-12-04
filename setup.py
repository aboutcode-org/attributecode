#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

from glob import glob
import io
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='attributecode',
    version='0.0.0',
    license='Apache-2.0',
    description=(
        ''
    ),
    long_description=(
        ''
    ),
    author='Chin-Yeung Li',
    author_email='info@nexb.com',
    url='https://github.com/nexB/attributecode',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
    ],
    keywords=[
        'attribution'
    ],
    install_requires=[
        'jinja2 >= 2.9, < 3.0',

        'click',

        "backports.csv ; python_version<'3.6'",

        # required by saneyaml
        'PyYAML >= 3.11, <=3.13',
        'saneyaml',

        'boolean.py >= 3.5, < 4.0',
        'license_expression >= 0.94',
        'packageurl_python >= 0.9.0',
    ],
    extras_require={
        ":python_version < '3.6'": ['backports.csv'],
    },
    entry_points={
        'console_scripts': [
            'attributecode=attributecode.cmd:attributecode',
        ]
    },
)
