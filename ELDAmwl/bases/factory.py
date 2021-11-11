# -*- coding: utf-8 -*-
"""base Classes for operations and operators"""
from prefect import Task

from ELDAmwl.component.interface import ICfg
from ELDAmwl.component.interface import IDataStorage
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.interface import ILogger
from ELDAmwl.component.interface import IParams
from ELDAmwl.component.registry import registry
from zope import component


class BaseOperationFactory(object):
    """
    Base class of operations.

    Base class of operations, returns an instance of a
    BaseOperation. If several alternative BaseOperation
    classes are available, the factory decides,
    which one to provide. This decision is based on options
    in the database or whether user defined plugins are available.

    If arguments or keywords are provided,
    they are automatically passed to the BaseOperation instance.
    """
    name = 'BaseFactory'

    def __init__(self):
        self.data_storage = component.queryUtility(IDataStorage)

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


class BaseOperation(Task):
    """
    Base class of operations
    """
    _params = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.data_storage = component.queryUtility(IDataStorage)
        super(BaseOperation, self).__init__()

    def init(self):
        pass

    @property
    def db_func(self):
        return component.queryUtility(IDBFunc)

    @property
    def _logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    @property
    def params(self):
        """
        Return the params
        :returns: The params
        """
        return component.queryUtility(IParams)

    # @params.setter
    # def params(self, value):
    #     """
    #     Set the params
    #     :param value: The params. Usually an instance of a
    #                   class derived from Params
    #     """
    #     self._params = value
