# -*- coding: utf-8 -*-
from ELDAmwl.component.interface import ICfg
from ELDAmwl.component.interface import ILogger
from ELDAmwl.database.tables.system_product import SystemProduct
from ELDAmwl.errors.exceptions import DBErrorTerminating
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from zope import component


class DBUtils(object):

    engine = None
    session = None

    def __init__(self, connect_string=None):
        self.connect_string = connect_string
        self.init_engine()

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    def get_connect_string(self):
        if self.connect_string:
            return self.connect_string
        result = 'mysql+pymysql://{user}:{passw}@{host}/{db}'.format(
            user=self.cfg.DB_USER,
            passw=self.cfg.DB_PASS,
            host=self.cfg.DB_SERVER,
            db=self.cfg.DB_DB)
        return result

    def init_engine(self):
        self.engine = create_engine(self.get_connect_string())

        # create a configured "Session" class
        self.session = sessionmaker(bind=self.engine)()

    def test_db(self):
        tasks = self.session.query(SystemProduct)
        try:
            _first_task = tasks.first()  # noqa F841
        except OperationalError as e:
            self.logger.error(""""Database cannot be reached! Please check the database connection
                            and the db connection settings in your _config.py\n{}""".format(e))
            raise DBErrorTerminating

#    def read_tasks(self, measurement_id):
#        tasks = self.session.query(  # Measurements,
#                                   SystemProduct)
        # .filter(SystemProduct._system_ID == Measurements._hoi_system_ID)
#        for task in tasks:
#            pass
#        measurements = self.Base.classes.measurements
#        sypro = self.Base.classes.system_product
#        psf = self.Base.classes.prepared_signal_files

        # products_query = self.session.query(measurements, sypro).\
        #     filter(measurements.ID == measurement_id).\
        #     filter(sypro._system_ID == measurements._hoi_system_ID).all()
        #
        # for products in products_query:
        #     product_id = products.system_product._Product_ID
        #
        #     psf_query = self.session.query(psf).\
        #         filter(psf._Meas_ID == measurement_id).\
        #         filter(psf._Product_ID == product_id).all()
        #
        #     if psf_query == []:
        #         logger.notice('no file for product {p_id}'.
        #                       format(p_id=product_id))
        #     else:
        #         for filenames in psf_query:
        #             logger.notice(product_id, filenames.filename)
