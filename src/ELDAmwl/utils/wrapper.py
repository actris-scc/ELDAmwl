# Wrapper to transform e.g. function signatures
from ELDAmwl.errors.exceptions import SciPyWrapperAxisError


def scipy_reduce_wrapper(scipy_func):
    """
    There is an scipy bug that makes scipy capable of dealing with one dimensional statistical functions, only.
    scipy.stats.stats.py:2425  n = a.shape[axis]

    This a wrapper wraps a scipy funtion and fixes the axis argument if given as tuple to a single axis number
    """

    def wrapper(arr, axis=None, **kwargs):
        """Check for the type of axis and transform to int"""
        if isinstance(axis, tuple):
            if len(axis) == 1:
                axis_scipy = axis[0]  # we hve a single axis just use this first element
            else:
                raise SciPyWrapperAxisError  # we have more than one axis, raise an error
        elif isinstance(axis, int):
            axis_scipy = axis  # we assume that
        else:
            raise SciPyWrapperAxisError  # Unknown axis type detected. Raise an error
        # call the wrapped function
        return scipy_func(arr, axis_scipy, **kwargs)

    return wrapper
