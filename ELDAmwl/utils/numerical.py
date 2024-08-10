from copy import deepcopy
from ELDAmwl.errors.exceptions import IntegrationFailed
from ELDAmwl.utils.constants import NEG_TEST_STD_FACTOR
from ELDAmwl.utils.wrapper import scipy_reduce_wrapper
from scipy.integrate import cumulative_trapezoid
from scipy.stats import sem

import numpy as np
import xarray as xr


def np_datetime64_to_datetime(np_datetme_64):
    return np_datetme_64.astype('M8[ms]').astype('O')


def rolling_mean_sem(data, level):
    """calculate rolling mean and stderror of mean"""
    means = data.rolling(level=level).reduce(np.mean)
    # the use of scipy_reduce_wrapper is needed to deal with incompatible axis types
    sems = data.rolling(level=level).reduce(scipy_reduce_wrapper(sem))
    return means, sems


def calc_rolling_means_sems(ds, w_width):
    ww0 = w_width[0, 0]
    # calculate rolling means, std errs of mean, and rel sem
    # if window_width are equal for all time slices,
    # get means and sems at once
    if np.all(w_width == ww0):
        means, sems = rolling_mean_sem(ds.data, ww0)

    # else do it for each time slice separately
    else:
        m_list = []
        s_list = []
        for t in range(ds.dims.time):
            mean, sems = rolling_mean_sem(ds.data[t], w_width[t, 0])
            m_list.append(mean)
            s_list.append(sems)

        means = xr.concat(m_list, 'time')
        sems = xr.concat(s_list, 'time')

    return means, sems


def find_minimum_window(means, sems, w_width, error_threshold):
    rel_sem = sems / means

    # find all means with rel_sem < error threshold:
    # rel_sem.where(rel_sem.data < error_threshold)
    #           => rel_sem values and nans
    # rel_sem.where(rel_sem.data < error_threshold) / rel_sem
    #           => ones and nans
    # valid_means = means and nans
    valid_means = (rel_sem.where((rel_sem.data < error_threshold) & (means.data > 0)) / rel_sem * means)

    # min_idx is the last bin of rolling window with smallest mean
    win_last_idx = np.nanargmin(valid_means.data, axis=1)
    win_first_idx = (win_last_idx[:] - w_width[:, 0])

    return win_first_idx, win_last_idx


def closest_bin(data, error=None, first_bin=None, last_bin=None, search_value=None):
    """
    finds the bin which has the value closest to the search value

    Args:
        data(np.array) : 1-dimensional vertical profile of the data
        error(np.array): vertical profile of absolute data errors. Default = None
                        if provided: if the closest bin is not equal to the search value within its error, returns None.
        first_bin, last_bin (int): first and last bin of the profile, where the search shall be done.
                                Default: None => the complete profile is used
        search_value (float): Default=None. if not provided, the mean value of the profile is used
    returns:
        idx (int): the index which has the value closest to the search value

    """

    result = None

    if first_bin is None:
        first_bin = 0
    if last_bin is None:
        last_bin = data.size

    _data = data[first_bin:last_bin]
    if error is not None:
        _error = error[first_bin:last_bin] * NEG_TEST_STD_FACTOR

    if search_value is not None:
        _search_value = search_value
    else:
        _search_value = np.nanmean(_data)

    diff = np.absolute(_data - _search_value)

    # if all points in search interval are further from search value than their errors
    if error is not None:
        if np.all(abs(_data[:] - search_value) > _error):
            return None

        success = False
        trials = 0
        while (not success) and trials < diff.size:
            min_idx = np.argmin(diff)
            if diff[min_idx] < _error[min_idx]:
                success = True
            else:
                diff[min_idx] = np.nanmax(diff)
                trials += 1
    else:
        min_idx = np.argmin(diff)

    if first_bin is not None:
        result = first_bin + min_idx
    else:
        result = min_idx

    # if error is not None:
    #     if abs(data[result] - search_value) > error[result]:
    #         result = None
    return result


def integral_profile(data,
                     range_axis=None,
                     extrapolate_ovl_factor=None,
                     first_bin=None,
                     last_bin=None):
    """
    calculates the vertical integral of a profile

    uses the scipy.integrate.cumulative_trapezoid method.
    if there are nan values, they are removed before integration and the resulting cumulative integral
    will be interpolated to the original range axis.

    Args:
        data (ndarray, 1 dimensional): the ydata to be integrated
        range_axis (ndarray, 1 dimensional):  the xdata.
        first_bin (int, optional): (default = 0) the first bin of the integration
        last_bin (int, optional): (default = ydata.size) the last bin of the integration.
                            if last_bin < first_bin, the integration direction is reversed
        extrapolate_ovl_factor (float, optional): (default = None) if not None, the profile is extrapolated towards
                    the ground by inserting a new data point with values
                    range_new = 0, data_new = data[0] * extrapolate_ovl_factor


    Returns:

    """
    ydata = deepcopy(data)
    xdata = deepcopy(range_axis)

    if np.all(np.isnan(ydata)):
        return None

    if last_bin is None:
        lb = ydata.size
    else:
        lb = last_bin

    if first_bin is None:
        fb = 0
    else:
        fb = first_bin

    # if integration direction is downward -> flip data arrays and exchange fb, lb
    reverse = False
    if lb < fb:
        reverse = True
        xdata = np.flip(xdata)
        ydata = np.flip(ydata)

        lb = ydata.size - lb
        fb = ydata.size - fb - 1

    # use only  profile parts between first_bin and  last_bin
    ydata = ydata[fb:lb]
    xdata = xdata[fb:lb]

    # remove nan data points
    fill_nan = False
    orig_xdata = None
    if np.any(np.isnan(ydata)):
        fill_nan = True
        orig_xdata = xdata
        nan_idxs = np.where(np.isnan(ydata))
        ydata = np.delete(ydata, nan_idxs)
        xdata = np.delete(xdata, nan_idxs)

    # fill the overlap region with extrapolated values
    # this is done by inserting an additional point at
    # the beginning (if ascending range axis) or end (if descending range axis) of xdata and ydata arrays
    # the insert_pos is 0 or -1, respectively.
    # the new point has the values xdata= 0 and ydata = ydata[insert_pos] * extrapolate_ovl_factor
    # insert_pos = None
    if extrapolate_ovl_factor is not None:
        # if the range axis is ascending, insert at position 0
        if xdata[0] < xdata[-1]:
            xdata = np.insert(xdata, 0, np.array([0]))
            ydata = np.insert(ydata, 0, np.array(ydata[0]) * extrapolate_ovl_factor)
        # if range axis is descending, append at the end
        else:
            xdata = np.append(xdata, np.array([0]))
            ydata = np.append(ydata, np.array(ydata[-1]) * extrapolate_ovl_factor)

    # calculate cumulative integral
    if ydata.size > 0:
        result = cumulative_trapezoid(ydata, x=xdata, initial=0)
    else:
        raise IntegrationFailed(None)

    # add half first bin (covers the integral between x=0 and x[0])
    if ydata.size > 1:
        result = result + ydata[0] * xdata[0] / 2
    else:
        result = np.array([np.nan])

    # if integration direction is downward -> flip result and xdata
    # note: the integral is usually negative because the differential x axis is negative
    if reverse:
        result = np.flip(result)
        xdata = np.flip(xdata)
        if fill_nan:
            orig_xdata = np.flip(orig_xdata)

    # if nan data points were removed before integration, the result is interpolated
    # to the original range axis in order to ensure that it has the same shape as input data.
    # This step has to be done after flipping the result (in case of downward integration)
    # because np.interp requires monotonically increasing sample points.
    if fill_nan:
        result = np.interp(orig_xdata, xdata, result)
        del orig_xdata

    # if the overlap region was filled with extrapolated values,
    # an additional data point was inserted before integration.
    # If nan values have been removed, the original shape was restored
    # in the previous step (interpolation). Otherwise,
    # the additional bin of the integral array needs to be removed
    # to ensure that result has the same shape as input data.
    # In case of downward integration, the result array has been flipped 2 steps before.
    # Therefore, the additional bin is always at position 0
    if (extrapolate_ovl_factor is not None) and (not fill_nan):
        result = np.delete(result, 0)

    del xdata
    del ydata

    return result


def m_to_km(height):
    return height * 0.001


def km_to_m(height):
    return height * 1000


def calc_resolution(axis_array):
    result = None

    diff = np.diff(axis_array, axis=-1)

    if len(axis_array.shape) > 1:
        d0 = diff[:, 0].reshape(axis_array.shape[0], 1)
    else:
        d0 = diff[0]
    # reshape is needed to allow broadcasting of the 2 arrays

    if np.all(abs(diff[:] - d0) < 1e-10):
        result = d0

    return result


def get_rangebin_axis(range_axis):
    range_res = calc_resolution(range_axis)

    # the first range value is always at half range_res
    first_bin = int(((range_axis[0] - range_res / 2) / range_res).round())

    rangebin_axis = np.arange(first_bin, range_axis.size)

    return rangebin_axis
