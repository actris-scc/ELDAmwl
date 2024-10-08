# from ELDAmwl.backscatter.common.params import IterBscParams
# from ELDAmwl.backscatter.raman.params import RamanBscParams
# from ELDAmwl.extinction.params import ExtinctionParams
from ELDAmwl.errors.exceptions import BasicProductMissingForDerivedProduct
from ELDAmwl.products import ProductParams
from ELDAmwl.utils.constants import ERROR_METHODS
from ELDAmwl.component.interface import IParams

from zope import component

class AngstroemExpParams(ProductParams):

    def __init__(self):
        super(AngstroemExpParams, self).__init__()
        self.sub_params += ['lambda1_params', 'lambda2_params']
        self.lambda1_prod_id = None
        self.lambda2_prod_id = None

        self.min_BscRatio_for_AE = None

        self.lambda1_params = None
        self.lambda2_params = None


    def from_db(self, general_params):
        super(AngstroemExpParams, self).from_db(general_params)
        # global measurement params
        meas_params = component.queryUtility(IParams).measurement_params

        query = self.db_func.read_angstroem_exp_params(general_params.prod_id)
        self.lambda1_prod_id = query.lambda1_product_id
        self.lambda2_prod_id = query.lambda2_product_id
        self.general_params.error_method = ERROR_METHODS[query.error_method_id]  # noqa E501
        self.min_BscRatio_for_AE = query.min_BscRatio_for_AE

        # self. lambda1_params is a link to the parameters of the basic bsc or ext product
        self.lambda1_params = meas_params.product_list[str(self.lambda1_prod_id)]
        if self.lambda1_params == {}:
            self.logger.error(f'Product {self.lambda1_prod_id} is not attributed to this mwl product.'
                              f'but it is needed for lidar ratio {general_params.prod_id} ')
            raise BasicProductMissingForDerivedProduct(general_params.prod_id, self.lambda1_prod_id)

        # self. lambda2_params is a link to the parameters of the basic bsc or ext product
        self.lambda2_params = meas_params.product_list[str(self.lambda2_prod_id)]
        if self.lambda2_params == {}:
            self.logger.error(f'Product {self.lambda2_prod_id} is not attributed to this mwl product.'
                              f'but it is needed for lidar ratio {general_params.prod_id} ')
            raise BasicProductMissingForDerivedProduct(general_params.prod_id, self.lambda1_prod_id)

        # some consistency tests and harmonization of / with bsc and ext params
        basic_params = [self.lambda1_params, self.lambda2_params]

        self.harmonize_resolution_settings(basic_params)
        self.ensure_different_wavelength(basic_params)
        self.ensure_same_product_type(basic_params)
        self.get_valid_alt_range(basic_params)

    def assign_to_product_list(self, global_product_list):
        super(AngstroemExpParams, self).assign_to_product_list(
            global_product_list,
        )
        self.lambda1_params.assign_to_product_list(global_product_list)
        self.lambda2_params.assign_to_product_list(global_product_list)

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(AngstroemExpParams, self).to_meta_ds_dict(dct)
        # dct.data_vars.minimum_backscatter_ratio = self.min_BscRatio_for_LR
