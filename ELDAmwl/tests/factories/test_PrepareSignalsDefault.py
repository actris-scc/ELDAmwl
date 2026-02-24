import unittest

from ELDAmwl.config import register_config
from ELDAmwl.elda_mwl.elda_mwl import register_params
from ELDAmwl.log.log import register_logger
from ELDAmwl.prepare_signals import PrepareSignalsDefault
from ELDAmwl.storage.data_storage import register_datastorage
from ELDAmwl.tests.pickle_data import un_pickle_data
from ELDAmwl.utils.constants import RESOLUTIONS
from ELDAmwl.component.interface import IDataStorage
from zope import component


class Test(unittest.TestCase):

    data_name = 'PrepareSignalsDefault_20181017oh00'

    def setUp(self):
        # get state
        register_config(args=None)
        register_logger('20181017oh00')
        self.data = un_pickle_data(self.data_name)
        register_datastorage(self.data['data_storage'])
        register_params(self.data['measurement_params'])
        self.op = PrepareSignalsDefault(products=self.data['basic_products'])

    def test_prepare_signals(self):
        self.op.run()
        test_result = component.queryUtility(IDataStorage)

        # reference_data are the datastorage afer pre-processing
        reference_data = un_pickle_data('PrepareSignalsDefault_20181017oh00.result')['result']
        for res in RESOLUTIONS:
            for prod_param in self.data['basic_products']:
                prod_id_str = prod_param.prod_id_str
                for sig in reference_data.prepared_signals(prod_id_str, res):
                    ch_id_str = sig.channel_id_str
                    assert sig == test_result.prepared_signal(prod_id_str, ch_id_str, res)
