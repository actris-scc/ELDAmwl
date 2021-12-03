from copy import deepcopy

from ELDAmwl.utils.wrapper import scipy_reduce_wrapper
from scipy.stats import sem
from scipy.integrate import cumulative_trapezoid

import numpy as np
import xarray as xr


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
    valid_means = (rel_sem.where(rel_sem.data < error_threshold) / rel_sem * means)

    # min_idx is the last bin of rolling window with smallest mean
    win_last_idx = np.nanargmin(valid_means.data, axis=1)
    win_first_idx = (win_last_idx[:] - w_width[:, 0])

    return win_first_idx, win_last_idx


def closest_bin(data, error=None, first_bin=None, last_bin=None, search_value=None):
    """finds the bin which has the value closest to the search value
    Args:
        data(np.array) : vertical profile of the data
        error(np.array): vertical profile of absolute data errors. Default = None
                        if provided: if the closest bin is not equal to the search value within its error, returns None.
        first_bin, last_bin (int): first and last bin of the profile, where the search shall be done.
                                Default: None => the complete profile is used
        search_value (float): Default=None. if not provided, the mean value of the profile is used
    returns:
        idx (int): the index which has the value closest to the search value
    """

    if first_bin is not None:
        _data = data[first_bin:]
    else:
        _data = data
    if last_bin is not None:
        _data = data[: last_bin]
    else:
        _data = data

    if search_value is not None:
        _search_value = search_value
    else:
        _search_value = np.nanmean(_data)

    diff = np.absolute(data - _search_value)
    min_idx = np.argmin(diff)

    if first_bin is not None:
        result = first_bin + min_idx
    else:
        result = min_idx

    if error is not None:
        if abs(data[min_idx] - search_value) > error [min_idx]:
            result = None

    return result

def integral_profile(data,
                     range=None,
                     quality_flag=None,
                     use_flags=None,
                     fill_overlap_region=None,
                     first_bin=None,
                     last_bin=None):
    """
    calculates the vertical integral of a profile
    Args:

    Returns:

    """
    data_cp = deepcopy(data)

    ydata = data_cp.values

    if range is None:
        xdata = data_cp.altitude.values
    else:
        xdata = deepcopy(range).values

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

    # remove data points with flags different from 'good' flags
    filter_flags = False
    if (use_flags is not None) and (quality_flag is not None):
        filter_flags = True
        fdata = deepcopy(quality_flag).values[fb:lb]
        for qf in use_flags:
            pass

    # calculate cumulative integral
    result = cumulative_trapezoid(ydata, x=xdata, initial=0)

    # if integration direction is downward, the integral is negative
    # because the differential x axis is negative -> flip result and invert sign
    if reverse:
        result = result * -1
        result[0] = 0
        result = np.flip(result)

    if fill_overlap_region is not None:
        result = result + (xdata[0] * ydata[0])

    del xdata
    del ydata
    if filter_flags:
        del fdata

    return result

