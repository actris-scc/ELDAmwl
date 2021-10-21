from ELDAmwl.factories.backscatter_factories.backscatter_calibration import FindBscCalibrWindowAsInELDA
from ELDAmwl.storage.data_storage import register_datastorage
from ELDAmwl.tests.pickle_data import un_pickle_data
from numpy import array_equal

import unittest


class Test(unittest.TestCase):

    data_name = 'FindBscCalibrWindowAsInELDA'

    def setUp(self):
        # get state
        self.data = un_pickle_data(self.data_name)
        register_datastorage(self.data['data_storage'])
        self.op = FindBscCalibrWindowAsInELDA(bsc_params=self.data['bsc_params'])
        self.op.init()

    def test_run(self):
        self.op.run()

    def test_get_bp_calibration_window(self):
        bp = self.data['bsc_params'][-1]
        calibration_window = self.op.find_calibration_window(bp)
        res = calibration_window

        data = un_pickle_data('FindBscCalibrWindowAsInELDA.find_calibration_window')

        assert array_equal(res, data['result'])
