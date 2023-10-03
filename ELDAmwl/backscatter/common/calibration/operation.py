from addict import Dict
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.database.tables.backscatter import BscCalibrMethod
from ELDAmwl.errors.exceptions import BscCalParamsNotEqual
from ELDAmwl.signals import Signals
from ELDAmwl.tests.pickle_data import write_test_data
from ELDAmwl.utils.constants import RBSC, NC_FILL_INT
from ELDAmwl.utils.numerical import calc_rolling_means_sems, m_to_km, km_to_m
from ELDAmwl.utils.numerical import find_minimum_window

from rayleigh_fit.rfit_SCC import r_fit

import numpy as np
import pandas as pd
import xarray as xr


class FindCommonBscCalibrWindow(BaseOperationFactory):
    """ fins a common calibration window for all bsc products

    Keyword Args:
        bsc_params (list of :class:`BackscatterParams`): \
                list of params of all backscatter products
    """
    name = 'FindCommonBscCalibrWindow'
    method_id = None

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'bsc_params' in kwargs
        self.method_id = kwargs['bsc_params'][0].calibration_params.cal_range_search_algorithm

        res = super(FindCommonBscCalibrWindow, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use for finding the bsc calibration window

        Returns: name of the class for determining the calibration window
        """
        return self.db_func.read_algorithm(self.method_id, BscCalibrMethod)
        # return FindBscCalibrWindowAsInELDA.__name__


class FindBscCalibrWindow(BaseOperation):
    """base class for finding calibration windows for all bsc products"""

    data_storage = None
    bsc_params = None
    calibration_params = None
    name = None

    def init(self):
        self.bsc_params = self.kwargs['bsc_params']
        self.calibration_params = self.bsc_params[0].calibration_params
        self.check_calibr_params()

        write_test_data(
            self.name,
            cls=self.__class__,
            data_storage=self.data_storage,
            bsc_params=self.bsc_params,
        )

    def check_calibr_params(self):
        # check whether all calibration params are equal
        for bp in self.bsc_params[1:]:
            if not self.calibration_params.equal(bp.calibration_params):
                self.logger.error(f'calibration params are not equal')
                raise BscCalParamsNotEqual(self.bsc_params[0].prod_id,
                                           bp.prod_id)

    def get_calibr_window_properties(self, bsc_param):
        """
        Args:
            bsc_param (BackscatterParams): Backscatter params

        Returns:
            ds : The dataset to operate on (= sig in search range for calibration window)
            w_width : The window widths [bins]
            error_threshold : The error threshold
            el_sig.range_axis : The range_axis axis to use
        """

        el_sig = self.data_storage.prepared_signal(bsc_param.prod_id_str,
                                                   bsc_param.total_sig_id_str)
        error_threshold = bsc_param.quality_params.error_threshold.highrange

        if bsc_param.general_params.product_type == RBSC:
            r_sig = self.data_storage.prepared_signal(
                bsc_param.prod_id_str, bsc_param.raman_sig_id_str)
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

        return ds, w_width, error_threshold

    def create_calibration_window_dataarray(self, ds,
                                            win_first_idx, win_last_idx,
                                            win_bottom_height,
                                            win_top_height):
        """
        Create a backscatter calibration window

        Args:
            ds : the dataset of the signal (contains the time and time_bounds variables)
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
        if (win_first_idx is not None) and (win_last_idx is not None):
            for t in range(ds.dims['time']):
                da[t, 0] = ds.height[t, win_first_idx[t]].values
                da[t, 1] = ds.height[t, win_last_idx[t]].values
        elif (win_bottom_height is not None and win_top_height is not None):
            da[:, 0] = win_bottom_height[:]
            da[:, 1] = win_top_height[:]


        return da


class FindBscCalibrWindowWithRaylFit(FindBscCalibrWindow):
    """find bsc calibration windows with Rayleigh fit

    """

    name = 'FindBscCalibrWindowWithRaylFit'
    all_results = None
    channels = []
    bad_channels = []
    window_widths = []
    window_width_default = None
    time_dim = 0
    elast_signals = None

    def run_a_rayl_fit(self, sig):
        channel_id = sig.channel_id_str

        if channel_id not in self.all_results.keys():

            # the Rayleigh fit routine expects as input:
            #   * range axis in km
            #   * background corrected signal (not range corrected)
            #   * Rayleigh backscatter signal which is attenuated by molecular scattering and 1/r² dependency

            range_axes = m_to_km(sig.range)
            range_sqr = range_axes ** 2
            range_res = (range_axes[:, 1] - range_axes[:, 0])

            rayl_ext = sig.ds.mol_extinction
            transm_up = sig.ds.mol_trasm_at_emission_wl
            transm_down = sig.ds.mol_trasm_at_detection_wl
            rayl_lr = sig.ds.mol_lidar_ratio
            attn_rayl_bsc = rayl_ext * transm_up * transm_down / rayl_lr / range_sqr
            signal = sig.data / range_sqr

            # ==== generate test output ====
            # (rayl_ext * transm_up * transm_down / rayl_lr)[0].to_dataframe(name='rayl_bsc').to_csv('dummy.csv')
            # sig.data[0].to_dataframe(name='signal').to_csv('dummy.csv')

            for t in range(sig.ds.dims['time']):
                input_data = Dict({'r': range_axes.values[t],
                                   'raylSig': attn_rayl_bsc.values[t],
                                   'Signal': signal.values[t],
                                   'rangebin': range_res.values[t],
                                   })

                start_height = m_to_km(self.calibration_params.cal_interval.min_height)
                top_height = m_to_km(self.calibration_params.cal_interval.max_height)
                self.window_width_default = m_to_km(self.calibration_params.window_width)

                # if the required window width is not in the predefined list -> add it
                self.window_widths = self.cfg.window_widths
                if not self.window_width_default in self.window_widths:
                    self.window_widths = self.window_widths.append(self.window_width_default)

                fit_results = r_fit(input_data,
                                    lower_range_limit_r=start_height,
                                    upper_range_limit_r=top_height,
                                    windows=self.window_widths,
                                    rsem_min=0.1,
                                    extended_output=True)

                # ==== generate test output ====
                # res = r_fit(input_data,
                #               lower_range_limit_r=start_height, upper_range_limit_r=top_height,
                #               windows=self.window_widths, rsem_min=0.1)
                # output for origin indeces
                # res.fit_rangebin, res.fit_window_rangebins, int(res.fit_rangebin - res.fit_window_rangebins/2)+2, int(res.fit_rangebin + res.fit_window_rangebins /2)+2

                for w in self.window_widths:
                    df = fit_results.profiles[w]
                    self.all_results[w][channel_id][t] = df[df.ALL == 1]
                    # ==== generate test output ====
                    # df[df.ALL == 1].to_csv('flags.csv')

    def check_results_of_channel(self, channel):
        w = 0
        has_result = False
        while (not has_result) and (w < len(self.window_widths)):
            wwidth = self.window_widths[w]
            for t in range(self.time_dim):
                if self.all_results[wwidth][channel][t].shape[0] > 0:
                    has_result = True
            w += 1
        if not has_result:
            self.logger.warning(f'could not find any calibration for channel {channel}.')
            self.bad_channels.append(channel)

    def find_best_compromise(self):
        win_center_ranges = np.ones(self.time_dim) * np.nan
        win_widths = np.ones(self.time_dim) * np.nan

        # check if one channel has no results at all
        for channel in self.channels:
            self.check_results_of_channel(channel)
        use_channels = list(set(self.channels).difference(set(self.bad_channels)))

        first_chan = use_channels[0]

        for t in range(self.time_dim):
            # 1) try to find a common calibration for default window width
            wwidth = self.window_width_default
            valid_heights = set(self.all_results[wwidth][first_chan][t].range)
            for channel in use_channels[1:]:
                valid_heights.intersection_update(set(self.all_results[wwidth][channel][t].range))

            if len(valid_heights) == 0:
                self.logger.warning(f'could not fine calibration for time slice {t} and window width {wwidth}')

                # 2) if not successful, try all other window widths
                w = 0
                while (len(valid_heights) == 0) and w < len(self.window_widths):
                    wwidth = self.window_widths[w]
                    valid_heights = set(self.all_results[wwidth][first_chan][t].range)
                    for channel in use_channels[1:]:
                        valid_heights.intersection_update(set(self.all_results[wwidth][channel][t].range))
                    w += 1

            if len(valid_heights) == 0:
                self.logger.warning(f'could not find any calibration for time slice {t}')
            else:
                # if overlapping calibration heights were found
                # -> find the height bin with the lowest average value of rsem
                valid_data = []
                for channel in self.channels:
                    df = self.all_results[wwidth][channel][t]
                    valid_data.append(df[df['range'].isin(list(valid_heights))]['Comb'])
                # ==== generate test output ====
                # valid_data = {}
                # for channel in self.channels:
                #     df = self.all_results[wwidth][channel][t]
                #     valid_data[channel] = df[df['range'].isin(list(valid_heights))]['Comb']
                # valid_data['height'] = list(valid_heights)
                # pd.DataFrame(valid_data).to_csv('/home/ina/workspace/temp/flags_comb.csv')

                best_idx = pd.concat(valid_data, axis=1, keys=self.channels).mean(axis=1).idxmin()
                win_center_ranges[t] = km_to_m(float(df[df.index == best_idx]['range']))
                win_widths[t] = km_to_m(wwidth)

        return win_center_ranges, win_widths

    def get_all_single_fits(self):
        self.all_results = Dict()
        self.elast_signals = Dict()

        for bp in self.bsc_params:
            sigs = self.data_storage.elpp_signals(bp.prod_id_str)
            for sig in sigs:
                if sig.is_elast_sig:
                    self.elast_signals[bp] = sig
                    self.channels.append(sig.channel_id_str)
                    self.time_dim = sig.ds.dims['time']
                    self.run_a_rayl_fit(sig)

    def get_cal_height_windows(self, bp, win_center_ranges, win_widths):

        sig = self.elast_signals[bp]

        # the result of the Rayleigh fit routine is the range value of the center of the best fit window
        # for further retrievals, we need the calibration window in height coordinates

        # 1) convert list of win_center_ranges into DataArray
        centers = xr.DataArray(np.array(win_center_ranges),
                               coords=[sig.ds.time],
                               dims=['time'])

        # 2) find the idx of the center bin
        center_idxs = sig.ranges_to_levels(centers)

        # the following steps work only for centers which are not nan
        # 3) initialize arrays with nan values
        win_center_heights = xr.ones_like(centers) * np.nan
        half_win_widths = xr.ones_like(centers) * np.nan
        win_bottom_heights = xr.ones_like(centers) * np.nan
        win_top_heights = xr.ones_like(centers) * np.nan

        # 4) find valid time slices (Rayleigh fit successful -> center is not nan)
        if centers.isnull().any():
            valid_ts = np.where(~np.isnan(centers))[0]
        else:
            valid_ts = range(centers.size)

        # 5) get the height value of this bins
        win_center_heights[valid_ts] = sig.height[valid_ts, center_idxs[valid_ts]].values

        # 6) calculate height boundaries of the windows
        half_win_widths[valid_ts] = win_widths[valid_ts] / 2
        win_bottom_heights[valid_ts] = win_center_heights[valid_ts] - half_win_widths[valid_ts]
        win_top_heights[valid_ts] = win_center_heights[valid_ts] + half_win_widths[valid_ts]

        # 7) generate DataArray with correct time dimension
        calibration_window = self.create_calibration_window_dataarray(
            sig.ds, None, None, win_bottom_heights, win_top_heights)

        return calibration_window

    def run(self):
        """
        Returns: common calibration window, but results are assigned to individual BackscatterParams, too
        """
        self.logger.debug('find backscatter calibration window with Rayleigh fit')
        self.init()
        # todo: check if calibration window is below maximum height of product (maybe the test is already there?
        # todo: in case that 1 signal (product) has a very low max height, -> go to different procedure for finding common cal window

        self.get_all_single_fits()
        win_center_ranges, win_widths = self.find_best_compromise()

        for bp in self.bsc_params:
            calibration_window = self.get_cal_height_windows(bp, win_center_ranges, win_widths)
            bp.calibr_window = calibration_window

        return calibration_window


class FindBscCalibrWindowAsInELDA(FindBscCalibrWindow):
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

    def find_calibration_window(self, bsc_param):

        # get the parameters for the rolling mean calculation
        data_set, w_width, error_threshold = self.get_calibr_window_properties(bsc_param)

        # calculate the rolling means and standard errors of the means (sems) with the given window properties
        means, sems = calc_rolling_means_sems(data_set, w_width)

        # find the min/max indexes of the window with the minimum data
        win_first_idx, win_last_idx = find_minimum_window(means, sems, w_width, error_threshold)

        # Create a calibration window from win_first_idx, win_last_idx
        calibration_window = self.create_calibration_window_dataarray(data_set, win_first_idx, win_last_idx, None, None)

        # Store the calibration window
        bsc_param.calibr_window = calibration_window

        write_test_data(
            'FindBscCalibrWindowAsInELDA.find_calibration_window',
            func=self.find_calibration_window,
            result=calibration_window,
        )

        return calibration_window

    # def init(self):
    #     super(FindBscCalibrWindowAsInELDA, self).init()
    #
    #     write_test_data(
    #         'FindBscCalibrWindowAsInELDA',
    #         cls=FindBscCalibrWindowAsInELDA,
    #         data_storage=self.data_storage,
    #         bsc_params=self.bsc_params,
    #     )

    def run(self):
        """
        Returns: None (results are assigned to individual BackscatterParams)
        """
        self.logger.debug('find backscatter calibration window as in ELDA')

        self.init()

        for bp in self.bsc_params:
            self.find_calibration_window(bp)

        return None


registry.register_class(FindCommonBscCalibrWindow,
                        FindBscCalibrWindowAsInELDA.__name__,
                        FindBscCalibrWindowAsInELDA)

registry.register_class(FindCommonBscCalibrWindow,
                        FindBscCalibrWindowWithRaylFit.__name__,
                        FindBscCalibrWindowWithRaylFit)
