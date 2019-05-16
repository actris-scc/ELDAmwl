import pytest
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.factory import BaseOperation
from ELDAmwl.registry import Registry


class TestFactory(BaseOperationFactory):
    pass


class TestOperationA(BaseOperation):
    pass


class TestOperationB(BaseOperation):
    pass


@pytest.fixture(scope="module")
def db(request):
    data = [
        ('TestA', TestOperationA),
        ('TestB', TestOperationB),
    ]
    return data

def test_factory_registration():

    registry = Registry()
    registry.register_class(TestFactory, 'TestA', TestOperationA)
    registry.register_class(TestFactory, 'TestB', TestOperationB)

    assert len(registry.factory_registry[TestFactory.name]) == 2
    assert registry.factory_registry[TestFactory.name]['TestA'] == TestOperationA
    assert registry.factory_registry[TestFactory.name]['TestB'] == TestOperationB
    assert registry.find_class_by_name(TestFactory, 'TestA') == TestOperationA
    assert registry.find_class_by_name(TestFactory, 'TestB') == TestOperationB


def test_factory(db, mocker):

    from ELDAmwl.registry import registry

    for klass_name, klass in db:
        registry.register_class(TestFactory, klass_name, klass)

    for klass_name, klass in db:

        mocker.patch.object(TestFactory, 'get_classname_from_db', return_value=klass_name)

        assert TestFactory()() == klass
