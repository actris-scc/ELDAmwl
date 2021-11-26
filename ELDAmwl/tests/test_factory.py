# -*- coding: utf-8 -*-
"""Tests for Signals"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import Registry
from unittest.mock import patch

import unittest


class Factory(BaseOperationFactory):
    pass


class OperationA(BaseOperation):
    pass


class OperationB(BaseOperation):
    pass


DB_DATA = [
    ('TestA', OperationA),
    ('TestB', OperationB),
]


def test_factory_registration():

    registry = Registry()
    registry.register_class(Factory, 'TestA', OperationA)
    registry.register_class(Factory, 'TestB', OperationB)

    assert len(registry.factory_registry[Factory.name].registry) == 2
    assert registry.get_factory_registration(Factory).find_class_by_name('TestA') == OperationA  # noqa E501
    assert registry.get_factory_registration(Factory).find_class_by_name('TestB')  == OperationB  # noqa E501
    assert registry.find_class_by_name(Factory, 'TestA') == OperationA
    assert registry.find_class_by_name(Factory, 'TestB') == OperationB


class TestFactory(unittest.TestCase):

    @patch.object(Factory, 'get_classname_from_db')
    def test_factory(self, mock_get_classname_from_db):

        from ELDAmwl.component.registry import registry

        for klass_name, klass in DB_DATA:
            registry.register_class(Factory, klass_name, klass)

        for klass_name, klass in DB_DATA:

            mock_get_classname_from_db.return_value = klass_name

            assert Factory()().__class__ == klass
