Configuration
=============

The configuration of ELDAmwl is handled in the
:mod:`ELDAmwl.configs` package.

All required configuration parameter are provided in the
``config_default.py`` module.

Some of the parameter there are just place holders,
e.g. for paths or database credentials. You need to
provide those information in a ``config.py``
module which is specific for your server.

.. code:: python

    # -*- coding: utf-8 -*-

    from ELDAmwl.configs.config_default import *

    # ===================
    # user specific configurations in this file
    # override configs in config_default.py
    # ===================

    # ===================
    # Directories
    # ===================

    LOG_PATH = 'c:/myPath'

.. note::
    All information provided in your specific ``config.py``
    will overwrite the corresponding values in the ``config_default.py``.

    You may modify also settings for the processing like
    maximum allowable smoothing.

