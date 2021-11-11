# -*- coding: utf-8 -*-
"""Tests for Signals"""

from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import Registry


class Factory(BaseOperationFactory):
    _name = 'Factory'


class OperationA(BaseOperation):
    pass


class OperationB(BaseOperation):
    pass


def test_registry_register():

    registry = Registry()
    registry.register_class(Factory, 'This is a test', OperationA)

    assert len(registry.factory_registry) == 1
    assert len(registry.factory_registry[Factory.name].registry) == 1
    assert registry.factory_registry[Factory.name].find_class_by_name('This is a test') == OperationA  # noqa E501
    assert registry.find_class_by_name(Factory, 'This is a test') == OperationA  # noqa E501

    registry.register_class(Factory, 'This is an override', OperationB, override=True)  # noqa E501

    assert len(registry.factory_registry) == 1
    assert len(registry.factory_registry[Factory.name].registry) == 3

    assert registry.factory_registry[Factory.name].find_class_by_name('This is an override') == OperationB  # noqa E501
    assert registry.find_class_by_name(Factory, 'This is an override') == OperationB  # noqa E501

    assert registry.factory_registry[Factory.name].find_class_by_name('This is a test') == OperationB  # noqa E501
    assert registry.find_class_by_name(Factory, 'This is a test') == OperationB  # noqa E501

    assert registry.status() == """Factory
    This is a test => <class 'ELDAmwl.tests.test_registry.OperationA'>
    This is an override => <class 'ELDAmwl.tests.test_registry.OperationB'>
    __OVERRIDE__ => This is an override"""
