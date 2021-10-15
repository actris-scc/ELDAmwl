

import unittest

from zope import component

from ELDAmwl.component.interface import IDBConstructor
from ELDAmwl.database.db_functions import register_db_func
from ELDAmwl.log.log import register_logger
from ELDAmwl.main import Main
from ELDAmwl.tests.database.create_test_db import register_dbconstructor, TEST_CONNECT_STRING


class TestTestDB(unittest.TestCase):
    def setUp(self):
        register_logger('None')
        register_dbconstructor()

    def test_test_db(self):
        db_constructor = component.queryUtility(IDBConstructor)
        db_constructor.run()


class Test(unittest.TestCase):

    def setUp(self):
        register_logger('None')
        register_dbconstructor()
        db_constructor = component.queryUtility(IDBConstructor)
        db_constructor.run()
        register_db_func(TEST_CONNECT_STRING)

    def test_20181017oh00(self):
        Main().elda('20181017oh00')

