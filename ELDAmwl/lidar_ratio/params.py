from ELDAmwl.component.interface import IParams
from ELDAmwl.products import ProductParams
from ELDAmwl.utils.constants import ERROR_METHODS
from zope import component


class LidarRatioParams(ProductParams):

    def __init__(self):
        super(LidarRatioParams, self).__init__()
        self.sub_params += ['backscatter_params', 'extinction_params']
        self.bsc_prod_id = None
        self.ext_prod_id = None
        self.min_BscRatio_for_LR = None

        self.extinction_params = None
        self.backscatter_params = None

    def from_db(self, general_params):
        super(LidarRatioParams, self).from_db(general_params)
        # global measurement params
        meas_params = component.queryUtility(IParams).measurement_params

        query = self.db_func.read_lidar_ratio_params(general_params.prod_id)
        self.bsc_prod_id = query.raman_backscatter_options_product_id
        self.ext_prod_id = query.extinction_options_product_id
        self.general_params.error_method = ERROR_METHODS[query.error_method_id]  # noqa E501
        self.min_BscRatio_for_LR = query.min_BscRatio_for_LR

        # self. backscatter_params is a link to the parameters of the basic bsc product
        self.backscatter_params = meas_params.product_list[str(self.bsc_prod_id)]

        # self. extinction_params is a link to the parameters of the basic ext product
        self.extinction_params = meas_params.product_list[str(self.ext_prod_id)]

        # use emission wavelength of ext product also for this lr
        self.general_params.emission_wavelength = self.backscatter_params.general_params.emission_wavelength

        # some consistency tests and harmonization of / with bsc and ext params
        basic_params = [self.backscatter_params, self.extinction_params]
        self.harmonize_resolution_settings(basic_params)
        self.ensure_same_wavelength(basic_params)
        self.get_valid_alt_range(basic_params)

    def assign_to_product_list(self, global_product_list):
        super(LidarRatioParams, self).assign_to_product_list(
            global_product_list,
        )
        self.backscatter_params.assign_to_product_list(global_product_list)
        self.extinction_params.assign_to_product_list(global_product_list)

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(LidarRatioParams, self).to_meta_ds_dict(dct)   # ToDo Ina debug
        # dct.data_vars.minimum_backscatter_ratio = self.min_BscRatio_for_LR
