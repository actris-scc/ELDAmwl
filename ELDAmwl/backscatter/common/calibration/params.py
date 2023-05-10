from addict import Dict
from ELDAmwl.bases.base import Params
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.output.mwl_file_structure import MWLFileStructure
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from zope.component import queryUtility


class BscCalibrationParams(Params):

    def __init__(self):
        super(BscCalibrationParams, self).__init__()
        self.cal_range_search_algorithm = None
        self.window_width = None
        self.cal_value = None
        self.cal_interval = Dict({'min_height': None,
                                 'max_height': None})

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        db_func = queryUtility(IDBFunc)
        query = db_func.get_bsc_cal_params_query(general_params.prod_id, general_params.product_type)

        result.cal_range_search_algorithm = \
            query.BscCalibrRangeSearchMethod.method_id
        result.window_width = \
            float(query.BscCalibrWindow.width)
        result.cal_value = \
            float(query.BscCalibrValue.bsc_ratio)
        result.cal_interval['min_height'] = \
            float(query.BscCalibrLowestHeight.height)
        result.cal_interval['max_height'] = \
            float(query.BscCalibrUpperHeight.height)

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
