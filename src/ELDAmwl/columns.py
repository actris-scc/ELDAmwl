import xarray as xr

from ELDAmwl.constants import T0

class Columns(object):
    """
    base column class (1 dimensional)
    """
    def __init__(self):
        self.ds = xr.Dataset()

    #result.data.coords['time'][0].values

    # @classmethod
    # def create_with_data(cls, in_data, header_info):
    #     result = cls()
    #
    #     result.ds = in_data
    #     try:
    #         result.header.attrs = header_info.attrs.copy()
    #     except BaseException:
    #         result.header.attrs = header_info.copy()
    #
    #     return result

    def relative_error(self):
        return self.err[:] / self.data[:]

    @property
    def data(self):
        return self.ds.data

    @property
    def err(self):
        return self.ds.err

    @property
    def rel_err(self):
        return self.relative_error()

    @property
    def cf(self):
        return self.ds.cf

    @property
    def altitude(self):
        return self.ds.altitude # altitude axis in m a.s.l.

    @property
    def height(self):
        return self.altitude - self.station_altitude # height axis in m a.g.
