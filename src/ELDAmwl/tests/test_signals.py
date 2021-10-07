# -*- coding: utf-8 -*-
"""Tests for Signals"""
from ELDAmwl.data_storage import DataStorage
from ELDAmwl.products import ProductParams
from ELDAmwl.signals import Signals

import os
import xarray as xr


# Where are the python files for testing
TEST_FILE_PATH = os.path.split(__file__)[0]

# where are the test data
TEST_DATA_PATH = os.path.join(TEST_FILE_PATH, 'data')

# test file 1 for intermediate nc file
TEST_INTERMEDIATE_FILE_1 = os.path.join(
    TEST_DATA_PATH,
    '20181228oh00_0000379.nc',
)


def test_Signals_from_nc_file():
    nc_ds = xr.open_dataset(TEST_INTERMEDIATE_FILE_1)
    for channelidx in range(2):
        Signals.from_nc_file(nc_ds, channelidx)


def test_signals_register(mocker):
    storage = DataStorage()

    mocker.patch.object(
        ProductParams,
        'prod_id_str',
        return_value='379',
    )
    params = ProductParams()

    nc_ds = xr.open_dataset(TEST_INTERMEDIATE_FILE_1)
    testsig = Signals.from_nc_file(nc_ds, 0)

    testsig.register(storage, params)
