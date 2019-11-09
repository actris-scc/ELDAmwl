from ELDAmwl.backscatter_factories import BackscatterParams
from ELDAmwl.base import Params
from ELDAmwl.extinction_factories import ExtinctionParams
from ELDAmwl.products import ProductParams


class LidarRatioParams(ProductParams):

    def __init__(self):
        super(LidarRatioParams, self).__init__()
        self.sub_params += ['backscatter_params', 'extinction_params']
        self.extinction_params = None
        self.backscatter_params = None

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params
        result.backscatter_params = BackscatterParams.from_db(general_params)
        result.extinction_params = ExtinctionParams.from_db(general_params)
        return result
