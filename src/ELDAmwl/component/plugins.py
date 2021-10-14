# -*- coding: utf-8 -*-
"""import of all plugins"""
from ELDAmwl.configs.config import PLUGINS_DIR

import glob
import importlib


def register_plugins():
    plugins = glob.glob(PLUGINS_DIR + '/*.py')
    for plugin in plugins:
        importlib.import_module(plugin)
