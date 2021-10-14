from ELDAmwl.errors.exceptions import SciPyWrapperAxisError
from ELDAmwl.utils.wrapper import scipy_reduce_wrapper

import unittest


def scipy_func(_a, axis=None, **_kwargs):
    return axis


class TestWrapper(unittest.TestCase):

    def test_good_tupel(self):
        assert scipy_reduce_wrapper(scipy_func)(5, axis=(2,)) == 2

    def test_bad_tupel(self):
        with self.assertRaises(SciPyWrapperAxisError):
            _x = scipy_reduce_wrapper(scipy_func)(5, axis=())
        with self.assertRaises(SciPyWrapperAxisError):
            _x = scipy_reduce_wrapper(scipy_func)(5, axis=(1, 2))  # noqa F841

    def test_int(self):
        assert scipy_reduce_wrapper(scipy_func)(5, axis=3) == 3

    def test_other_type(self):
        with self.assertRaises(SciPyWrapperAxisError):
            _x = scipy_reduce_wrapper(scipy_func)(5)
        with self.assertRaises(SciPyWrapperAxisError):
            _x = scipy_reduce_wrapper(scipy_func)(5, axis='time')  # noqa F841
