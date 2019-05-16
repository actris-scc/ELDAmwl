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

        self.valid_alt_range = AttrDict({'first': None, 'last': None})

    @classmethod
    def from_query(cls, query):
        result = cls()

        result.prod_id = query.Products.ID

        return result
