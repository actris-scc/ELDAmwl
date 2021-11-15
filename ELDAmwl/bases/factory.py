# -*- coding: utf-8 -*-
"""base Classes for operations and operators"""
from inspect import currentframe, getframeinfo, getmodulename

from ELDAmwl.component.interface import ICfg, IGraph
from ELDAmwl.component.interface import IDataStorage
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.interface import ILogger
from ELDAmwl.component.interface import IParams
from ELDAmwl.component.registry import registry
from zope import component


class Inspect:

    _shape = 'box'
    _instance_count = {}

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    def __init__(self, parent_class):
        self.parent_class = parent_class
        if self.__class__.__name__ not in Inspect._instance_count:
            Inspect._instance_count[self.__class__.__name__] = 1
        self.instance_count = Inspect._instance_count[self.__class__.__name__]
        Inspect._instance_count[self.__class__.__name__] += 1
        self.inspect()

    def inspect(self):
        current_frame = currentframe()
        caller_frame = current_frame.f_back

        while caller_frame:
            try:
                caller_instance = caller_frame.f_locals['self']
            except KeyError:
                caller_frame = caller_frame.f_back
                continue

            if self.parent_found(caller_instance):
                if type(caller_instance) != type(self):
                    caller_instance = caller_frame.f_locals['self']
                    parent_label = self.instance_label(caller_instance)
                    child_label = self.instance_label(self)

                    if 'SlopeToExt' in child_label:
                        a=7
                    print(f'{parent_label} -> {child_label}')
                    self.to_dot(caller_instance)
                    break
                # else:
                #     print(f'{type(self).__name__}.{function}')

            caller_frame = caller_frame.f_back

    def instance_label(self, instance):
        result = type(instance).__name__

        if self.cfg.GRAPH_INSTANCES:
            result += f'({instance.instance_count})'

        return result

    def parent_found(self, caller_instance):
        return isinstance(caller_instance, self.parent_class)

    def to_dot(self, caller_instance):
        dot = component.queryUtility(IGraph)
        parent = self.instance_label(caller_instance)
        child = self.instance_label(self)
        dot.node(parent, shape=caller_instance._shape)
        dot.node(child, shape=self._shape)
        dot.edge(parent, child)


class BaseOperationFactory(Inspect):
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
    _shape = 'box'

    def __init__(self):
        super(BaseOperationFactory, self).__init__(BaseOperation)
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


class BaseOperation(Inspect):
    """
    Base class of operations
    """
    _params = None
    _shape = 'ellipse'
    _instance_count = {}

    def __init__(self, **kwargs):
        super(BaseOperation, self).__init__(BaseOperationFactory)
        self.kwargs = kwargs
        self.data_storage = component.queryUtility(IDataStorage)

    def parent_found(self, caller_instance):
        if isinstance(caller_instance, self.parent_class):
            return True
        return isinstance(caller_instance, self.parent_class) or isinstance(caller_instance, BaseOperation)

    def init(self):
        pass

    @property
    def db_func(self):
        return component.queryUtility(IDBFunc)

    @property
    def logger(self):
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
