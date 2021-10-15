

import unittest

from zope import component

from ELDAmwl.component.interface import IDBConstructor
from ELDAmwl.log.log import register_logger
from ELDAmwl.main import Main
from ELDAmwl.tests.database.create_test_db import register_dbconstructor


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


    def test_20181017oh00(self):
        Main().elda('20181017oh00')

