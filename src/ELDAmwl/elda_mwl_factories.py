from ELDAmwl.base import Params
from ELDAmwl.database.db_functions import read_system_id, get_products_query, read_mwl_product_id
from ELDAmwl.product_params import ProductParams
from ELDAmwl.registry import registry
from ELDAmwl.factory import BaseOperationFactory, BaseOperation


class MeasurementParams(Params):
    """
    Those are general parameters of the measurement
    """
    def __init__(self, measurement_id):
        self.meas_id = measurement_id
        self.system_id = read_system_id(self.meas_id)
        self.mwl_product_id = read_mwl_product_id(self.system_id)
        self.products = []

    def read_product_list(self):
        p_query = get_products_query(self.mwl_product_id)
        for q in p_query:
            self.products.append(ProductParams.from_query(q))



class RunELDAmwl(BaseOperation):
    """
    This is the global ELDAmwl operation class
    """

    def __init__(self, measurement_id):
        self.params = MeasurementParams(measurement_id)

    def read_tasks(self):
        self.params.read_product_list()
