

from ELDAmwl.component.interface import IDBConstructor
from ELDAmwl.database.db_functions import register_db_func
from ELDAmwl.main import elda_setup_components
from ELDAmwl.main import Main
from ELDAmwl.storage.data_storage import register_datastorage
from ELDAmwl.tests.database.create_test_db import register_dbconstructor
from ELDAmwl.tests.database.create_test_db import TEST_CONNECT_STRING
from zope import component

import unittest


class TestTestDB(unittest.TestCase):
    def setUp(self):
        elda_setup_components()
        register_dbconstructor()

    def test_test_db(self):
        db_constructor = component.queryUtility(IDBConstructor)
        db_constructor.run()


class Test(unittest.TestCase):

    def setUp(self):
        elda_setup_components(env='testing')
        register_dbconstructor()
        db_constructor = component.queryUtility(IDBConstructor)
        db_constructor.run()
        # Bring up the global db_access
        register_db_func(TEST_CONNECT_STRING)
        # Bring up the global data storage
        register_datastorage()

    def test_20181017oh00(self):
        Main().elda('20181017oh00')
