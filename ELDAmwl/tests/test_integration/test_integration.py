from addict import Dict
from ELDAmwl.component.interface import IDBConstructor
from ELDAmwl.config import register_config
from ELDAmwl.database.db_functions import register_db_func
from ELDAmwl.elda_mwl.elda_mwl import register_params
from ELDAmwl.log.log import register_logger
from ELDAmwl.main import Main
from ELDAmwl.monte_carlo.operation import register_monte_carlo
from ELDAmwl.storage.data_storage import register_datastorage
from ELDAmwl.tests.database.create_test_db import register_dbconstructor
from ELDAmwl.tests.database.create_test_db import TEST_CONNECT_STRING
from zope import component

import os
import unittest


class TestTestDB(unittest.TestCase):
    def setUp(self):
        print(os.getcwd())
        register_config(args=None, env='testing')
        # Setup the logging facility for this measurement ID
        register_logger('20181017oh00')
        register_dbconstructor()

    def test_test_db(self):
        db_constructor = component.queryUtility(IDBConstructor)
        db_constructor.run()


class Test(unittest.TestCase):

    def setUp(self):
        print(os.getcwd())
        register_config(args=None, env='testing')
        register_logger('20181017oh00')
        register_dbconstructor()
        db_constructor = component.queryUtility(IDBConstructor)
        db_constructor.run()
        # Bring up the global db_access
        register_db_func(TEST_CONNECT_STRING)
        # Bring up the global data storage
        register_datastorage()
        # Bring up the global params
        register_params()
        # Bring up Monte Carlo Adapter
        register_monte_carlo()

    def test_20181017oh00(self):
        Main().elda(
            Dict({'meas_id': '20181017oh00'}))
