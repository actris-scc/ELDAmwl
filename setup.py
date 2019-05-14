# -*- coding: utf-8 -*-
"""Installer for the ELDAmwl package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='ELDAmwl',
    version='0.1',
    description='ELDA multi wavelengt SCC module',
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    ],
    keywords='Python Plone',
    author='Ina',
    author_email='ina@ina-mattis.de',
    url='https://pypi.python.org/pypi/ELDAmwl',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=[],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'setuptools',
        'netcdf4',
        'sqlalchemy',
        'colorlog',
        'pymysql',
        'flake8',
        'isort',
        'flake8-isort',
        'flake8-blind-except',
        'flake8-coding',
        'flake8-commas',
        'flake8-debugger',
        'flake8-deprecated',
        'flake8-isort',
        'flake8-pep3101',
        'flake8-print',
        'flake8-quotes',
        'flake8-string-format',
        'flake8-todo',
        'pytest',
        'attrdict',
    ],
    extras_require={
        'test': [
        ],
    },
    entry_points="""
    """,
)
