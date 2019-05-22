from ELDAmwl.constants import T0

class Column(object):
    """
    base column class (1 dimensional)
    """
    def __init__(self):
        self.start_time = T0
        self.stop_time = T0

        # the 1 dimensional data array
        self._data = None
        # the  1 dimensional array of absolute errors, same dimension as _data
        self._err = None
        # the 1 dimensional array of valid/invalid flags, same dimension as _data
        self._valid = None
        # the 1 dimensional array of cloud flags, same dimension as _data
        self._cf = None

    # @classmethod
    # def create_with_data(cls, in_data, header_info):
    #     result = cls()
    #
    #     result._data = in_data
    #     try:
    #         result.header.attrs = header_info.attrs.copy()
    #     except BaseException:
    #         result.header.attrs = header_info.copy()
    #
    #     return result

    def relative_error(self):
        return self.err[:] / self.data[:]

    @property
    def size(self):
        return self._data.size

    @property
    def data(self):
        return self._data

    @property
    def err(self):
        return self._err

    @property
    def rel_err(self):
        return self.relative_error()

    @property
    def cf(self):
        return self._cf

    @property
    def valid(self):
        return self._valid
