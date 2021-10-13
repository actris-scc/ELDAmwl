# -*- coding: utf-8 -*-
"""base Classes for factories and operators"""
from zope import component

from ELDAmwl.component.interface import IDBFunc, ILogger
from ELDAmwl.component.registry import registry


try:
    import ELDAmwl.configs.config as cfg  # noqa E401
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg  # noqa E401


class BaseOperationFactory(object):
    """
    Base class of factories.

    Base class of factories, returns an instance of a
    BaseOperation. If several alternative BaseOperation
    classes are available, the factory decides,
    which one to provide. This decision is based on options
    in the database or whether user defined plugins are available.

    If arguments or keywords are provided,
    they are automatically passed to the BaseOperation instance.
    """
    name = 'BaseFactory'

    def __call__(self, *args, **kwargs):
        klass = self.get_class()
        res = klass(*args, **kwargs)
        return res

    @property
    def db_func(self):
        return component.queryUtility(IDBFunc)

    def get_classname_from_db(self):
        raise NotImplementedError

    def get_class(self):
        klass_name = self.get_classname_from_db()
        klass = registry.find_class_by_name(self.__class__, klass_name)
        return klass


class BaseOperation(object):
    """
    Base class of operations
    """
    _params = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def init(self):
        pass

    @property
    def db_func(self):
        return component.queryUtility(IDBFunc)

    @property
    def logger(self):
        return component.queryUtility(ILogger)


    @property
    def params(self):
        """
        Return the params
        :returns: The params
        """
        return self._params

    @params.setter
    def params(self, value):
        """
        Set the params
        :param value: The params. Usually an instance of a
                      class derived from Params
        """
        self._params = value
