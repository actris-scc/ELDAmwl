from ELDAmwl.base import Params
from attrdict import AttrDict


class ProductParams(Params):
    """
    general parameters for product retrievals
    """

    def __init__(self):
        # product id
        self.prod_id = None
        self.product_type = None

        self.is_basic_product = False
        self.is_derived_product = False

        self.calc_with_hr = False
        self.calc_with_lr = False

        self.error_method = None
        self.detection_limit = None
        self.error_threshold = AttrDict({'low': None, 'high': None})

        self.valid_alt_range = AttrDict({'min_height': None, 'max_height': None})

    @classmethod
    def from_query(cls, query):
        result = cls()

        result.prod_id = query.Products.ID
        result.product_type = query.Products._prod_type_ID

        result.is_basic_product = query.ProductTypes.is_basic_product
        result.is_derived_product = ~ result.is_basic_product

#        result.error_method = query.ProductOptions.
        result.error_threshold.low = query.ErrorThresholdsLow.value
        result.error_threshold.high = query.ErrorThresholdsHigh.value
        result.detection_limit = query.ProductOptions.detection_limit

        result.valid_alt_range.min_height = query.ProductOptions.min_height
        result.valid_alt_range.max_height = query.ProductOptions.max_height


        return result
