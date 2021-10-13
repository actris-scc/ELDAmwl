import unittest

import numpy as np
from numpy import array_equal

from ELDAmwl.factories.backscatter_factories import FindBscCalibrWindowAsInELDA
from ELDAmwl.tests.pickle_data import un_pickle_data


class Test(unittest.TestCase):

    data_name = 'FindBscCalibrWindowAsInELDA'

    def setUp(self):
        # get state
        self.data = un_pickle_data(self.data_name)
        self.op = FindBscCalibrWindowAsInELDA(
            data_storage = self.data['data_storage'],
            bsc_params = self.data['bsc_params']
        )
        self.op.init()

        # get results

    def test_run(self):
        self.op.run()

    def test_get_bp_calibration_window(self):
        bp = self.data['bsc_params'][0]
        calibration_window = self.op.get_bp_calibration_window(bp)
        res = calibration_window.data

#        ref_data = self.get_bp_calibration_window_ref(bp)
        ref = np.array(
            [[5880.64007628, 6419.32466342],
            [4773.34398049, 5312.02856763]]
        )
        assert array_equal(res, ref)




