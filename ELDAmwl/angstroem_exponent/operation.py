# -*- coding: utf-8 -*-
"""Classes for angstroem exponent calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.angstroem_exponent.product import AngstroemExps
from ELDAmwl.utils.constants import MC  # ToDo needed?
from ELDAmwl.utils.constants import NC_FILL_INT  # ToDo needed?
from ELDAmwl.utils.constants import NC_FILL_STR  # ToDo needed?

import numpy as np
import zope


class AngstroemExpFactory(BaseOperationFactory):
    """
    """

    name = 'AngstroemExpFactory'

    def __call__(self, **kwargs):
        assert 'ae_param' in kwargs
        assert 'resolution' in kwargs
        res = super(AngstroemExpFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'lidarRatioFactoryDefault' .
        """
        return AngstroemExpFactoryDefault.__name__


class AngstroemExpFactoryDefault(BaseOperation):
    """
    derives a single instance of :class:`AngstroemExps`.
    """

    name = 'angstroemExpFactoryDefault'

    param = None
    resolution = None
    ext = None
    bsc = None
    empty_ae = None
    result = None
    prod_id = None

    def prepare(self):
        self.param = self.kwargs['ae_param']
        self.resolution = self.kwargs['resolution']
        self.prod_id = self.param.prod_id_str

        # lambda1 and lambda2 are deep copies from the data storage
        self.lambda1 = self.data_storage.basic_product_common_smooth(self.param.lambda1_prod_id, self.resolution)
        self.lambda2 = self.data_storage.basic_product_common_smooth(self.param.lambda2_prod_id, self.resolution)

        self.empty_ae = AngstroemExps.init(self.lambda1, self.lambda2, self.param, self.resolution)

    def get_non_merge_product(self):
        # create Dict with all params which are needed for the calculation
        ae_params = Dict({
            'error_method': self.param.error_method,
            'min_bsc_ratio': self.param.min_BscRatio_for_AE,
        })

        ae_routine = CalcAngstroemExp()(
            prod_id=self.prod_id,
            lambda1=self.lambda1,
            lambda2=self.lambda2,
            ae_params=ae_params,
            empty_ae=self.empty_ae)

        ae = ae_routine.run()

        if self.param.error_method == MC:
            adapter = zope.component.getAdapter(ae_routine, IMonteCarlo)
            self.result.err[:] = adapter(self.param.mc_params)
        else:
            ae = ae

        del self.lambda1
        del self.lambda2

        return ae

    def get_product(self):
        self.prepare()

        if not self.param.includes_product_merging():
            ae = self.get_non_merge_product()
        else:
            ae = None

        return ae


class CalcAngstroemExp(BaseOperationFactory):
    """
    creates a Class for the calculation of an Angstroem Exponent

    Returns an instance of BaseOperation which calculates the angstroem exponent
    from backscatter or extinction at two different wavelengths.
    In this case, it will be always an instance of CalcAngstroemExpDefault().

    Keyword Args:
        ae_params (:class:`ELDAmwl.angstroem_exponent.params.AngstroemExpParams`): \
                retrieval parameter of the angstroem exponent product
        lambda1 (:class:):     # ToDo complete
        lambda2 (:class:):     # ToDo complete
        empty_ae (:class:`ELDAmwl.angstroem_exponent.product.AngstroemExps`): \
                instance of AngstroemExps which has all meta data but profile data are empty arrays

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """

    name = 'CalcAngstroemExp'

    def __call__(self, **kwargs):
        assert 'ae_params' in kwargs
        assert 'lambda1' in kwargs
        assert 'lambda2' in kwargs
        assert 'empty_ae' in kwargs

        res = super(CalcAngstroemExp, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcAngstroemExpDefault' .
        """
        return 'CalcAngstroemExpDefault'


class CalcAngstroemExpDefault(BaseOperation):
    """
    Calculates angstroem exponent from backscatter or extinction at two different wavelengths.

    The result is a copy of empty_ae, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        ae_params (:class:`ELDAmwl.angstroem_exponent.params.AngstroemExpParams`): \
                retrieval parameter of the angstroem exponent product
        lambda1 (:class:``):  # ToDo complete
        lambda2 (:class:``): # ToDo change
        empty_ae (:class:`ELDAmwl.angstroem_exponents.product.AngstroemExps`): \
                instance of AngstroemExp which has all meta data but profile data are empty arrays

    Returns:
        angstroem exponent profiles (:class:`ELDAmwl.angstroem_exponent.product.AngstroemExps`)

    """

    name = 'CalcAngstroemExpDefault'

    lambda1 = None
    lambda2 = None
    result = None

    def __init__(self, **kwargs):
        self.lambda1 = kwargs['lambda1']
        self.lambda2 = kwargs['lambda2']
        self.result = deepcopy(kwargs['empty_ae'])

    def run(self, lambda1=None, lambda2=None):
        """
        run the angstrom exponent calculation

        The optional keyword args 'lambda1' and 'lambda2' allow to feed new input data into
        an existing instance of CalcAngstroemExtDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals # ToDo needed?

        Keyword Args:
            lambda1 (:class:``):    # ToDo complete
            lambda2 (:class:``):    # ToDo complete

        Returns:
            profiles of angstroem exponents (:class:`ELDAmwl.angstroem_exponent.product.AngstroemExps`)

        """
        if lambda1 is None:
            lambda1 = self.lambda1
        if lambda2 is None:
            lambda2 = self.lambda2

        # ToDo check the "order" of the wavelengths (bigger/smaller) not to invert the results. If needed, change them.
        # ToDo check formulas
        with np.errstate(invalid='ignore'):  # ToDo is this correct?
            self.result.ds['data'] = np.log(lambda1.data / lambda2.data) / np.log(
                lambda2.emission_wavelength.data / lambda1.emission_wavelength.data)
            self.result.ds['err'] = np.log(lambda2.emission_wavelength.data / lambda1.emission_wavelength.data) \
                * np.sqrt(np.power((lambda1.err / lambda1.data), 2) + np.power((lambda2.err / lambda2.data), 2))
            self.result.ds['qf'] = lambda2.qf | lambda1.qf

        return self.result


registry.register_class(CalcAngstroemExp,
                        CalcAngstroemExpDefault.__name__,
                        CalcAngstroemExpDefault)

registry.register_class(AngstroemExpFactory,
                        AngstroemExpFactoryDefault.__name__,
                        AngstroemExpFactoryDefault)
