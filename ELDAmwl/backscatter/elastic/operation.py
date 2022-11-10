from addict import Dict
from copy import deepcopy
from ELDAmwl.backscatter.common.operation import BackscatterFactory
from ELDAmwl.backscatter.common.operation import BackscatterFactoryDefault
from ELDAmwl.backscatter.elastic.product import ElastBackscatters
from ELDAmwl.backscatter.elastic.tools.operation import CalcElastBscProfile
from ELDAmwl.bases.base import DataPoint
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IElastBscOp
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.utils.constants import MC

import zope


class ElastBackscatterFactory(BackscatterFactory):
    """

    """

    name = 'ElastBackscatterFactory'

    def get_classname_from_db(self):
        return ElastBackscatterFactoryDefault.__name__


class ElastBackscatterFactoryDefault(BackscatterFactoryDefault):
    """
    derives a single instance of :class:`ElasticBackscatters`.
    """

    name = 'ElastBackscatterFactoryDefault'

    def prepare(self):
        super(ElastBackscatterFactoryDefault, self).prepare()

        self.empty_bsc = ElastBackscatters.init(
            self.elast_sig, self.param, self.calibr_window)

    def get_non_merge_product(self):

        bsc_retrieval_routine = CalcElastBackscatter()(
            bsc_params=self.param,
            calc_routine=CalcElastBscProfile()(prod_id=self.prod_id),
            calibr_window=self.calibr_window,
            elast_sig=self.elast_sig,
            empty_bsc=self.empty_bsc,
        )
        bsc = bsc_retrieval_routine.run()

        if self.param.error_method == MC:
            adapter = zope.component.getAdapter(bsc_retrieval_routine, IMonteCarlo)
            bsc.err[:] = adapter(self.param.mc_params)

        else:
            bsc = bsc

        return bsc


class CalcElastBackscatter(BaseOperationFactory):
    """
    creates a class for the calculation of an elastic backscatter coefficient

    Returns an instance of BaseOperation which calculates the particle
    backscatter coefficient from an elastic signal. In this case, it
    will be always an instance of CalcElastBackscatterDefault.

    Keyword Args:
        bsc_params (:class:`ELDAmwl.backscatter.elastic.params.ElastBscParams`): \
                retrieval parameter of the backscatter product
        calibr_window (xarray.DataArray): variable 'backscatter_calibration_range' (time: 2, nv: 2) \
                contains bottom and top height of calibration window for each time slice
        calc_routine (:class:`ELDAmwl.bases.factory.BaseOperation`):
            result of :class:`ELDAmwl.backscatter.elastic.tools.operation.CalcElastBscProfile`
        elast_signal (:class:`ELDAmwl.signals.Signals`): time series of elastic signal profiles
        empty_bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): \
                instance of RamanBackscatters which has all meta data but profile data are empty arrays

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """

    name = 'CalcElastBackscatter'

    def __call__(self, **kwargs):
        assert 'bsc_params' in kwargs
        assert 'calibr_window' in kwargs
        assert 'calc_routine' in kwargs
        assert 'elast_sig' in kwargs
        assert 'empty_bsc' in kwargs

        res = super(CalcElastBackscatter, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcElastBackscatterDefault' .
        """
        return 'CalcElastBackscatterDefault'


@zope.interface.implementer(IElastBscOp)
class CalcElastBackscatterDefault(BaseOperation):
    """
    Calculates particle backscatter coefficient from an elastic signal.

    The result is a copy of empty_bsc, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        bsc_params (:class:`ELDAmwl.backscatter.raman.params.RamanBscParams`): \
                retrieval parameter of the backscatter product
        calibr_window (xarray.DataArray): variable 'backscatter_calibration_range' (time: 2, nv: 2) \
                contains bottom and top height of calibration window for each time slice
        calc_routine (:class:`ELDAmwl.bases.factory.BaseOperation`):
                    result of :class:`ELDAmwl.backscatter.elast.tools.operation.CalcElastBscProfile`
        elast_signal (:class:`ELDAmwl.signals.Signals`): elastic signal
        empty_bsc (:class:`ELDAmwl.backscatter.elastic.product.ElastBackscatters`): \
                instance of ElastBackscatters which has all meta data but profile data are empty arrays

    Returns:
        profiles of particle backscatter coefficients (:class:`ELDAmwl.backscatter.elastic.product.ElastBackscatters`)

    """

    name = 'CalcElastBackscatterDefault'

    bsc_params = None
    elast_sig = None
    calibr_window = None
    calc_routine = None
    result = None

    def __init__(self, **kwargs):
        super(CalcElastBackscatterDefault, self).__init__(**kwargs)
        self.elast_sig = self.kwargs['elast_sig']
        self.calibr_window = self.kwargs['calibr_window']
        self.calc_routine = self.kwargs['calc_routine']
        self.bsc_params = self.kwargs['bsc_params']
        self.result = deepcopy(self.kwargs['empty_bsc'])

    def run(self, data=None):
        """
        run the Elast backscatter calculation

        The the optional keyword arg 'data' allows to feed new signals into
        an existing instance of CalcElastBackscatterDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals

        Keyword Args:
            data (:class:`ELDAmwl.signals.Signals`): elastic signals, default=None

        Returns:
            profiles of particle backscatter
            coefficients(:class:`ELDAmwl.backscatter.elastic.product.ElastBackscatters`)

        """
        if data is None:
            data = self.elast_sig

        # todo: self.calibr_window is hard coded here for testing. remove and check, why it is different from ELDA
        self.calibr_window[0, :] = [14529.52, 15008.35]
        cal_first_lev = data.heights_to_levels(
            self.calibr_window[:, 0])
        cal_last_lev = data.heights_to_levels(
            self.calibr_window[:, 1])

        # extract relevant parameter for calculation of elastic backscatter
        # from BackscatterParams into Dict

        calibr_value = DataPoint.from_data(
            self.bsc_params.calibration_params.cal_value, 0, 0)
        cal_params = Dict({'cal_first_lev': cal_first_lev.values,
                           'cal_last_lev': cal_last_lev.values,
                           'calibr_value': calibr_value})

        error_params = Dict({'err_threshold':
                            self.bsc_params.quality_params.error_threshold,
                             })

        # copy wavelength into data.ds, because only data.ds is provided to the calculation routine
        data.ds['emission_wavelength'] = data.emission_wavelength

        self.result.ds = self.calc_routine.run(
            elast_sig=data.ds,
            range_axis=data.range,
            error_params=error_params,
            calibration=cal_params,
        )
        self.result.ds['assumed_particle_lidar_ratio'] = deepcopy(data.ds.assumed_particle_lidar_ratio)
        self.result.ds['assumed_particle_lidar_ratio_error'] = deepcopy(data.ds.assumed_particle_lidar_ratio_error)
        self.result.ds['time_bounds'] = deepcopy(data.ds.time_bounds)
        self.result.ds['laser_pointing_angle'] = deepcopy(data.ds.laser_pointing_angle)

        return self.result


registry.register_class(CalcElastBackscatter,
                        CalcElastBackscatterDefault.__name__,
                        CalcElastBackscatterDefault)

registry.register_class(ElastBackscatterFactory,
                        ElastBackscatterFactoryDefault.__name__,
                        ElastBackscatterFactoryDefault)
