Installation
============

The handling of packages and the virtual environment is managed by poetry.

Installation on production system as user
-----------------------------------------

system requirements: pip, python3

1) install poetry

.. code:: console

    $ python3 -mpip install --user poetry


2) set <path>, where poetry puts the virtual environment

.. code:: console

    $ poetry config virtualenvs.path <path>

3) on slackware, it is necessary to set poetry installer type

.. code:: console

    $ poetry config experimental.new-installer  false

4) clone repository

.. code:: console

    $ git clone https://github.com/actris-scc/ELDAmwl.git

5) create new poetry project

.. code:: console

    $ poetry new eldamwl_run

6) add dependencies to pyproject.toml

.. code:: console

    $ cd eldamwl_run
    $ nano pyproject.toml

.. code:: console

    [tool.poetry.dependencies]
    python = "^3.8"
    ELDAmwl = { path = "../ELDAmwl/", develop = false }


7) install ELDAmwl

.. code:: console

    $ poetry install

8) activate virtual environment

.. code:: console

    $ poetry shell

update a new version on production system
-----------------------------------------

1) pull changes from repository

.. code:: console

    $ git pull https://github.com/actris-scc/ELDAmwl.git

2) if new packages have been added to new version in repository
.. code:: console

    $ poetry update

installation of a development system
------------------------------------
steps 1-4 from above

.. code:: console

    $ cd ELDAmwl
    $ poetry install

check whether installation was successfull
-----------------------------------------

.. code:: console

    $ poetry shell
    $ elda_mwl -h

or

.. code:: console

    $ poetry run elda_mwl -h
