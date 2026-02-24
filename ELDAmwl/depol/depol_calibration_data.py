from ELDAmwl.bases.base import DataPoint


class DepolarizationCalibration(object):
    gain_factor = None
    gain_factor_correction = None

    def copy(self):
        new = DepolarizationCalibration()
        new.gain_factor = self.gain_factor.copy()
        new.gain_factor_correction = self.gain_factor_correction.copy()
        return new

    def __eq__(self, other):
        if self.gain_factor != other.gain_factor:
            return False
        if self.gain_factor_correction != other.gain_factor_correction:
            return False
        return True

    @classmethod
    def from_nc_file(cls, nc_ds, pol_cal_idx):
        result = cls()
        result.gain_factor = \
            DataPoint.from_nc_file(nc_ds,
                                   'polarization_gain_factor',
                                   pol_cal_idx)

        result.gain_factor_correction = \
            DataPoint.from_nc_file(nc_ds,
                                   'polarization_gain_factor_correction',
                                   pol_cal_idx)
        # todo: how to handle the following info? are they needed?
        # polarization_gain_factor_measurementid
        # polarization_gain_factor_correction_start_datetime
        # seconds since 1970-01-01T00:00:00Z
        # polarization_gain_factor_correction_stop_datetime
        # polarization_gain_factor_correction_start_datetime
        # polarization_gain_factor_correction_stop_datetime
        return result


