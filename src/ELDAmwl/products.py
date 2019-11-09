from attrdict import AttrDict

from ELDAmwl.base import Params
from ELDAmwl.signals import Signals
from ELDAmwl.log import logger

class Products(Signals):

    def save_to_netcdf(self):
        pass


class ProductParams(Params):

    def __init__(self):
        self.sub_params = ['general_params']
        self.general_params = None

#    @classmethod
#    def from_db(cls, general_params):
#        pass


class GeneralProductParams(Params):
    """
    general parameters for product retrievals
    """

    def __init__(self):
        # product id
        self.prod_id = None
        self.product_type = None
        self.usecase = None

        self.is_basic_product = False
        self.is_derived_product = False

        self.calc_with_hr = False
        self.calc_with_lr = False

        self.error_method = None
        self.detection_limit = None
        self.error_threshold = AttrDict({'low': None, 'high': None})

        self.valid_alt_range = AttrDict({'min_height': None, 'max_height': None})

        self.ELPP_filename = ''

    @classmethod
    def from_query(cls, query):
        result = cls()

        result.prod_id = query.Products.ID
        result.product_type = query.Products._prod_type_ID
        result.usecase = query.Products._usecase_ID

        result.is_basic_product = query.ProductTypes.is_basic_product == 1
        result.is_derived_product = not result.is_basic_product

        result.error_threshold.low = query.ErrorThresholdsLow.value
        result.error_threshold.high = query.ErrorThresholdsHigh.value
        result.detection_limit = query.ProductOptions.detection_limit

        result.valid_alt_range.min_height = query.ProductOptions.min_height
        result.valid_alt_range.max_height = query.ProductOptions.max_height

        result.ELPP_filename = query.PreparedSignalFile.filename

        return result

    @classmethod
    def from_db(cls, general_params):
        if not isinstance(general_params, ProductParams):
            logger.error('')
            return None

        result = general_params.deepcopy()

        return result
