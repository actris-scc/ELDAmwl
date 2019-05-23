import os

from ELDAmwl.signals import Signals

# Where are the python files for testing
TEST_FILE_PATH = os.path.split(__file__)[0]

# where are the test data
TEST_DATA_PATH = os.path.join(TEST_FILE_PATH, 'data')

# test file 1 for intermediate nc file
TEST_INTERMEDIATE_FILE_1 = os.path.join(TEST_DATA_PATH, '20181228oh00_0000379.nc')

def test_Signals_from_nc_file():
    for channelidx in range(2):
        Signals.from_nc_file(TEST_INTERMEDIATE_FILE_1, channelidx)
