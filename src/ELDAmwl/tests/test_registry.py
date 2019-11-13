# -*- coding: utf-8 -*-
"""Tests for Signals"""

from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.registry import Registry


class Factory(BaseOperationFactory):
    name = 'Factory'


class OperationA(BaseOperation):
    pass


class OperationB(BaseOperation):
    pass


def test_registry_register():

    registry = Registry()
    registry.register_class(Factory, OperationA)

    assert len(registry.factory_registry) == 1
    assert len(registry.factory_registry[Factory.name].registry) == 1
    assert registry.factory_registry[Factory.name].find_class_by_name(OperationA.__class__.__name__) == OperationA  # noqa E501
    assert registry.find_class_by_name(Factory, OperationA.__class__.__name__) == OperationA  # noqa E501

    registry.register_class(Factory, OperationB, override=True)  # noqa E501

    assert len(registry.factory_registry) == 1
    assert len(registry.factory_registry[Factory.name].registry) == 3

    assert registry.factory_registry[Factory.name].find_class_by_name(OperationB.__class__.__name__) == OperationB  # noqa E501
    assert registry.find_class_by_name(Factory, OperationB.__class__.__name__) == OperationB  # noqa E501

    assert registry.factory_registry[Factory.name].find_class_by_name(OperationA.__class__.__name__) == OperationB  # noqa E501
    assert registry.find_class_by_name(Factory, OperationA.__class__.__name__) == OperationB  # noqa E501

    assert registry.status() == """Factory
    {0} => <class 'ELDAmwl.tests.test_registry.OperationA'>
    {1} => <class 'ELDAmwl.tests.test_registry.OperationB'>
    __OVERRIDE__ => This is an override""".format(OperationA.__class__.__name__, OperationB.__class__.__name__)
