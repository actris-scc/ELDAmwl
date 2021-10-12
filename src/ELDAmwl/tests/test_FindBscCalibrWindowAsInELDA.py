import unittest

from ELDAmwl.factories.backscatter_factories import FindBscCalibrWindowAsInELDA
from ELDAmwl.tests.pickle_data import un_pickle_data


class Test(unittest.TestCase):

    data_name = 'FindBscCalibrWindowAsInELDA'

    def setUp(self):
        self.data = un_pickle_data(self.data_name)

    def test_run(self):
        op = FindBscCalibrWindowAsInELDA(
            data_storage = self.data['data_storage'],
            bsc_params = self.data['bsc_params']
        )
        op.run()

