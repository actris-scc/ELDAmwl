# -*- coding: utf-8 -*-
"""import of all plugins"""
from ELDAmwl.component.interface import ICfg
from zope import component

import glob
import importlib


def register_plugins():
    cfg = component.queryUtility(ICfg)
    plugins = glob.glob(cfg.PLUGINS_DIR + '/*.py')
    for plugin in plugins:
        importlib.import_module(plugin)
