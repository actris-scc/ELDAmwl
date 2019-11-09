# -*- coding: utf-8 -*-
"""Tests for Signals"""

from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.registry import Registry


class TestFactory(BaseOperationFactory):
    name = 'TestFactory'


class TestOperation(BaseOperation):
    pass


def test_registry_register():

    registry = Registry()
    registry.register_class(TestFactory, 'This is a test', TestOperation)

    assert len(registry.factory_registry) == 1
    assert len(registry.factory_registry[TestFactory.name]) == 1
    assert registry.factory_registry[TestFactory.name]['This is a test'] == TestOperation  # noqa E501
    assert registry.find_class_by_name(TestFactory, 'This is a test') == TestOperation  # noqa E501
