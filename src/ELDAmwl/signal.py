import numpy as np
from ELDAmwl.column import Column


class Signal(Column):

    def __init__(self):
        self._emission_wavelength = np.nan
        self._detection_wavelength = np.nan
        self._channel_id = np.nan
        self._detection_type = np.nan
        self._channel_id_in_ncfile

    @classmethod
    def from_nc_file(cls, nc_file, idx_in_file):
        result = cls()


        return result

