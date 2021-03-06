# -*- coding: utf-8 -*-
"""Tests for the operations"""
from addict import Dict
from ELDAmwl.elda_mwl.elda_mwl import MeasurementParams


def test_MeasurementParams(mocker):
    # REALLY important! Patch where the function is imported
    # not where the function is defined!!!!!!
    mocker.patch(
        'ELDAmwl.elda_mwl_factories.read_system_id',
        return_value=0,
    )
    mocker.patch(
        'ELDAmwl.elda_mwl_factories.read_mwl_product_id',
        return_value=1,
    )

    val = Dict({'Products': Dict({'ID': 1})})

    mocker.patch(
        'ELDAmwl.elda_mwl_factories.get_products_query',
        return_value=[val],
    )

    measurement_params = MeasurementParams(4)
    measurement_params.read_product_list()

    assert measurement_params.system_id == 0

    assert measurement_params.mwl_product_id == 1
    assert measurement_params.products[0].prod_id == 1

    assert measurement_params.meas_id == 4

    pass
