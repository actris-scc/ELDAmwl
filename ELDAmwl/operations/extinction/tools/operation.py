from addict import Dict
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.utils.constants import NC_FILL_STR
from math import sqrt

import numpy as np


class LinFit(BaseOperation):
    """

    """
    name = 'LinFit'

    data = None

    def run(self, **kwargs):
        """

        Keyword Args:
            signal: addict.Dict with the keys 'x_data', 'y_data', 'yerr_data'
            which are all np.array
        Returns:
            addict.Dict with keys 'slope' and 'slope_err'

        """
        assert 'signal' in kwargs
        self.data = kwargs['signal']

        if self.kwargs['weight']:
            weight = 1 / self.data.yerr_data
        else:
            weight = None

        fit = np.polyfit(self.data.x_data, self.data.y_data,
                         1, w=weight, cov='unscaled')
        # np.polyfit(x, y, deg, w=weight)
        # weight: For gaussian uncertainties, use 1/sigma.
        # These settings (w= 1/err, cov='unscaled')correspond
        # to the equations from numerical
        # recipes which are implemented in the old ELDA
        #
        # fit[0]: Polynomial coefficients, highest power first
        # fit[1]: The covariance matrix of the polynomial
        #           coefficient estimates. The diagonal of this
        #           matrix are the variance estimates for
        #           each coefficient

        result = Dict({'slope': fit[0][0],
                       'slope_err': sqrt(fit[1][0, 0]),
                       })

        return result


class WeightedLinearFit(BaseOperation):
    """
    calculates a weighted linear fit

    """
    name = 'WeightedLinearFit'

    def __init__(self, **kwargs):
        super(WeightedLinearFit, self).__init__(**kwargs)
        self.fit = LinFit(weight=True)

    def run(self, **kwargs):
        """
        starts the fit

        Keyword Args:
            signal: addict.Dict with the keys 'x_data', 'y_data', \
            'yerr_data' which are all np.array

        Returns:
            addict.Dict with keys 'slope' and 'slope_err'

        """
        assert 'signal' in kwargs

        return self.fit.run(signal=kwargs['signal'])


class NonWeightedLinearFit(BaseOperation):
    """
    calculates a non-weighted linear fit

    """
    name = 'NonWeightedLinearFit'

    def __init__(self, **kwargs):
        super(NonWeightedLinearFit, self).__init__(**kwargs)
        self.fit = LinFit(weight=False)

    def run(self, **kwargs):
        """
        starts the fit

        Keyword Args:
            signal: addict.Dict with the keys 'x_data', \
            'y_data', 'yerr_data' which are all np.array

        Returns:
            addict.Dict with keys 'slope' and 'slope_err'

        """
        assert 'signal' in kwargs
        return self.fit.run(signal=kwargs['signal'])


class SignalSlope(BaseOperationFactory):
    """
    Creates a Class for the calculation of signal slope.

    Keyword Args:
        prod_id (str): id of the product
    """

    name = 'SignalSlope'
    prod_id = NC_FILL_STR  # Todo Ina into Base class???

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']

        res = super(SignalSlope, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which slope algorithm to use

        Returns: name of the class for the slope calculation
        """
        return self.db_func.read_extinction_algorithm(self.prod_id)


class SlopeToExtinction(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which calculates the particle
    extinction coefficient from signal slope. In this case, it
    will be always an instance of SlopeToExtinctionDefault().
    """

    name = 'SlopeToExtinction'

    def __call__(self, **kwargs):
        assert 'slope' in kwargs
        assert 'ext_params' in kwargs
        res = super(SlopeToExtinction, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'SlopeToExtinctionDefault' .
        """
        return 'SlopeToExtinctionDefault'


class SlopeToExtinctionDefault(BaseOperation):
    """
    Calculates particle extinction coefficient from signal slope.
    """

    name = 'SlopeToExtinctionDefault'

    def run(self):
        """
        """
        slope = self.kwargs['slope']
        ext_params = self.kwargs['ext_params']

        det_wl = ext_params.detection_wavelength
        em_wl = ext_params.emission_wavelength
        ang_exp = ext_params.angstroem_exponent

        wl_factor = 1. / (1. + pow((em_wl / det_wl), ang_exp))

        slope['data'] = -1. * slope.data * wl_factor
        slope['err'] = slope.err * wl_factor

        return None


registry.register_class(SignalSlope,
                        NonWeightedLinearFit.__name__,
                        NonWeightedLinearFit)

registry.register_class(SignalSlope,
                        WeightedLinearFit.__name__,
                        WeightedLinearFit)

registry.register_class(SlopeToExtinction,
                        SlopeToExtinctionDefault.__name__,
                        SlopeToExtinctionDefault)
