# -*- coding: utf-8 -*-
"""import of all plugins"""
import glob
from os.path import join
from ELDAmwl.configs.config import PLUGINS_DIR

def register_plugins():
    plugins = glob.glob(join(PLUGINS_DIR, 'plugins') + '/*.py')
    for plugin in plugins:
        import plugin
