from addict import Dict
from ELDAmwl.bases.base import Params
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import BscCalParamsNotEqual
from ELDAmwl.output.mwl_file_structure import MWLFileStructure
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.signals import Signals
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.numerical import calc_rolling_means_sems
from ELDAmwl.utils.numerical import find_minimum_window
from zope.component import queryUtility

import numpy as np
import xarray as xr


class BscCalibrationParams(Params):

    def __init__(self):
        super(BscCalibrationParams, self).__init__()
        self.cal_range_search_algorithm = None
        self.WindowWidth = None
        self.cal_value = None
        self.cal_interval = Dict({'min_height': None,
                                 'max_height': None})

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        db_func = queryUtility(IDBFunc)
        query = db_func.get_bsc_cal_params_query(general_params.prod_id, general_params.product_type)

        result.cal_range_search_algorithm = \
            query.BscCalibrOption.calRangeSearchMethod_ID
        result.window_width = \
            float(query.BscCalibrOption.WindowWidth)
        result.cal_value = \
            float(query.BscCalibrOption.calValue)
        result.cal_interval['min_height'] = \
            float(query.BscCalibrOption.LowestHeight)
        result.cal_interval['max_height'] = \
            float(query.BscCalibrOption.TopHeight)

        return result

    def equal(self, other):
        result = True
        if (self.cal_interval.min_height != other.cal_interval.min_height) or \
                (self.cal_interval.max_height != other.cal_interval.max_height) or \
                (self.window_width != other.window_width) or \
                (self.cal_value != other.cal_value) or \
                (self.cal_range_search_algorithm != other.cal_range_search_algorithm):
            result = False

        return result

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        mwl_struct = MWLFileStructure()
        mwl_vars = MWLFileVarsFromDB()
        dct.data_vars.calibration_range_search_algorithm = \
            mwl_vars.bsc_calibr_method_var(self.cal_range_search_algorithm)
        dct.data_vars.calibration_search_range = mwl_struct.cal_search_range_var(self.cal_interval)
        dct.data_vars.calibration_value = mwl_struct.bsc_calibr_value_var(self.cal_value)


class FindCommonBscCalibrWindow(BaseOperationFactory):
    """ fins a common calibration window for all bsc products

    Keyword Args:
        bsc_params (list of :class:`BackscatterParams`): \
                list of params of all backscatter products
    """
    name = 'FindCommonBscCalibrWindow'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'bsc_params' in kwargs
        res = super(FindCommonBscCalibrWindow, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        return FindBscCalibrWindowAsInELDA.__name__


class FindBscCalibrWindowAsInELDA(BaseOperation):
    """find bsc calibration windows as in ELDA

    * for all bsc products and time slices independently
    * the calibration window is the minimum interval for which \
      the relative standard error of the mean is smaller than the \
      error threshold for altitudes above 2km.
    * use signal ratio in case of Raman bsc, otherwise elastic signal only
    * the results are xr.DataArrays (with variable \
      'backscatter_calibration_range') which are assigned to the individual
      BackscatterParams.calibr_window
    """

    name = 'FindBscCalibrWindowAsInELDA'

    data_storage = None
    bsc_params = None

    def create_calibration_window_datarray(self, ds, height_axis, win_first_idx, win_last_idx):
        """
        Create a backscatter calibration window

        Args:
            ds : the dataset of the signal (contains the time and time_bounds variables)
            height_axis : The height axis of the elastic signal
            win_first_idx : The first indexes of the window
            win_last_idx : The last indexes of the window

        Returns:
            DataArray with bottom and top height [m a.g.] of the calibration window for each time slice.
        """
        da = xr.DataArray(
            np.zeros((ds.dims['time'], ds.dims['nv'])),
            coords=[ds.time, ds.nv],
            dims=['time', 'nv'])
        da.name = 'backscatter_calibration_range'
        da.attrs = {'long_name': 'height_axis range where '
                                 'calibration was calculated',
                    'units': 'm'}
        for t in range(ds.dims['time']):
            da[t, 0] = height_axis[t, win_first_idx[t]].values
            da[t, 1] = height_axis[t, win_last_idx[t]].values

        return da

    def get_rolling_window_properties(self, bsc_param):
        """
        Args:
            bsc_param (BackscatterParams): Backscatter params

        Returns:
            ds : The dataset to operate on
            w_width : The window widths [bins]
            el_sig.height_axis : The height_axis axis to use
            error_threshold : The error threshold
        """

        el_sig = self.data_storage.prepared_signal(bsc_param.prod_id_str,
                                                   bsc_param.total_sig_id)
        error_threshold = bsc_param.quality_params.error_threshold.highrange

        if bsc_param.general_params.product_type == RBSC:
            r_sig = self.data_storage.prepared_signal(
                bsc_param.prod_id_str, bsc_param.raman_sig_id)
            sigratio = Signals.as_sig_ratio(el_sig, r_sig)
            ds = sigratio.data_in_vertical_range(
                bsc_param.calibration_params.cal_interval)
        else:
            ds = el_sig.data_in_vertical_range(
                bsc_param.calibration_params.cal_interval)

        # width of window [bins] = width of calibration window [m] / raw resolution of signal [m]
        # window_width need to be rounded and converted to integer
        # number of bins used for sliding window operations (rolling) must be window_width +1
        # because those operations use slices [n:n+window_width]
        w_width = np.around(bsc_param.calibration_params.window_width / el_sig.raw_heightres).astype(int) + 1

        return ds, w_width, el_sig.height, error_threshold

    def find_calibration_window(self, bsc_param):

        # get the parameters for the rolling mean calculation
        data_set, w_width, height, error_threshold = self.get_rolling_window_properties(bsc_param)

        # calculate the rolling means and standard errors of the means (sems) with the given window properties
        means, sems = calc_rolling_means_sems(data_set, w_width)

        # find the min/max indexes of the window with the minimum data
        win_first_idx, win_last_idx = find_minimum_window(means, sems, w_width, error_threshold)

        # Create a calibration window from win_first_idx, win_last_idx
        calibration_window = self.create_calibration_window_datarray(data_set, height, win_first_idx, win_last_idx)

        # Store the calibration window
        bsc_param.calibr_window = calibration_window

        # write_test_data(
        #     func=self.find_calibration_window,
        #     result=calibration_window,
        # )
        return calibration_window

    def init(self):
        self.bsc_params = self.kwargs['bsc_params']

        # write_test_data(
        #     cls=FindBscCalibrWindowAsInELDA,
        #     data_storage=self.data_storage,
        #     bsc_params=self.bsc_params
        # )

    def run(self):
        """
        Returns: None (results are assigned to individual BackscatterParams)
        """
        self.init()

        # check whether all calibration params are equal
        for bp in self.bsc_params[1:]:
            if not self.bsc_params[0].calibration_params.equal(
                    bp.calibration_params):
                raise BscCalParamsNotEqual(self.bsc_params[0].prod_id,
                                           bp.prod_id)
        for bp in self.bsc_params:
            self.find_calibration_window(bp)

        return None


registry.register_class(FindCommonBscCalibrWindow,
                        FindBscCalibrWindowAsInELDA.__name__,
                        FindBscCalibrWindowAsInELDA)
