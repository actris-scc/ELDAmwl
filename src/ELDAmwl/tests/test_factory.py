# -*- coding: utf-8 -*-
"""Tests for Signals"""

from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.registry import Registry

import pytest


class Factory(BaseOperationFactory):
    pass


class OperationA(BaseOperation):
    pass


class OperationB(BaseOperation):
    pass


@pytest.fixture(scope='module')
def db(request):
    data = [
        ('TestA', OperationA),
        ('TestB', OperationB),
    ]
    return data


def test_factory_registration():

    registry = Registry()
    registry.register_class(Factory, 'TestA', OperationA)
    registry.register_class(Factory, 'TestB', OperationB)

    assert len(registry.factory_registry[Factory.name]) == 2
    assert registry.factory_registry[Factory.name]['TestA'] == OperationA  # noqa E501
    assert registry.factory_registry[Factory.name]['TestB'] == OperationB  # noqa E501
    assert registry.find_class_by_name(Factory, 'TestA') == OperationA
    assert registry.find_class_by_name(Factory, 'TestB') == OperationB


def test_factory(db, mocker):

    from ELDAmwl.registry import registry

    for klass_name, klass in db:
        registry.register_class(Factory, klass_name, klass)

    for klass_name, klass in db:

        mocker.patch.object(
            Factory,
            'get_classname_from_db',
            return_value=klass_name,
        )

        assert Factory()() == klass
