# -*- coding: utf-8 -*-
"""Installer for the ELDAmwl package."""

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
    packages=['ELDAmwl','ELDAmwl.bases'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'autodocsumm',
        'setuptools',
        'netcdf4',
        'sqlalchemy',
        'SQLAlchemy-Utils',
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
        'pytest-mock',
        'addict',
        'scipy',
        'sphinx',
        'sphinxcontrib-qthelp',
        'sphinxcontrib-serializinghtml',
        'sphinx-rtd-theme',
        'xarray',
    ],
    extras_require={
        'test': [
        ],
    },
    entry_points="""
    [console_scripts]
    create_test_db = ELDAmwl.tests.database.create_test_db
    """,

)
