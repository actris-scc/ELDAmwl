# -*- coding: utf-8 -*-
"""import of all plugins"""
import glob
import importlib
from ELDAmwl.configs.config import PLUGINS_DIR

def register_plugins():
    plugins = glob.glob(PLUGINS_DIR + '/*.py')
    for plugin in plugins:
        importlib.import_module(plugin)
