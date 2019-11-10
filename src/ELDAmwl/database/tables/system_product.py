# -*- coding: utf-8 -*-
"""Classes for measurement system-product related db tables"""

from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import Float
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class SystemProduct(Base):
    __tablename__ = 'system_product'

    ID = Column(INTEGER, primary_key=True)
    _system_ID = Column(INTEGER, nullable=False, index=True)
    _Product_ID = Column(INTEGER, nullable=False, index=True)


class MWLproductProduct(Base):
    __tablename__ = 'mwlproduct_product'

    ID = Column(INTEGER, primary_key=True)
    _mwl_product_ID = Column(INTEGER, nullable=False, index=True)
    _Product_ID = Column(INTEGER, nullable=False, index=True)
    create_with_hr = Column(INTEGER, nullable=False, index=False)
    create_with_lr = Column(INTEGER, nullable=False, index=False)


class Products(Base):
    __tablename__ = 'products'

    ID = Column(INTEGER, primary_key=True)
    _usecase_ID = Column(INTEGER)
    _prod_type_ID = Column(INTEGER, nullable=False, index=True)
    _hoi_stations_ID = Column('__hoi_stations__ID', CHAR(3))
    _hirelpp_product_option_ID = Column(INTEGER)


class ProductTypes(Base):
    __tablename__ = '_product_types'

    ID = Column(INTEGER, primary_key=True)
    product_type = Column(CHAR(100), nullable=False)
    # Changed to Nullable for csv import to work.
    better_name = Column(CHAR(100), nullable=True)
    nc_file_id = Column(CHAR(1), nullable=False)
    processor_ID = Column(INTEGER, nullable=False)
    # Changed to Nullable for csv import to work.
    is_mwl_only_product = Column(INTEGER, nullable=True)
    # Changed to Nullable for csv import to work.
    is_in_mwl_products = Column(INTEGER, nullable=True)
    # Changed to Nullable for csv import to work.
    is_basic_product = Column(INTEGER, nullable=True)


class ProductOptions(Base):
    __tablename__ = 'product_options'

    ID = Column(INTEGER, primary_key=True)
    _product_ID = Column(INTEGER, nullable=False)
    _lowrange_error_threshold_ID = Column(INTEGER, nullable=False, index=True)
    _highrange_error_threshold_ID = Column(INTEGER, nullable=False, index=True)
    detection_limit = Column(DECIMAL(11, 11), nullable=False)
    min_height = Column(DECIMAL(10, 4), nullable=False)
    max_height = Column(DECIMAL(10, 4), nullable=False)
    preprocessing_integration_time = Column(INTEGER, nullable=False)
    preprocessing_vertical_resolution = Column(DECIMAL(10, 4), nullable=False)
    interpolation_id = Column(INTEGER, nullable=False)


class ErrorThresholds(Base):
    __tablename__ = '_error_thresholds'

    ID = Column('Id', INTEGER, primary_key=True)
    value = Column(Float, nullable=False)
    name = Column(String(100), nullable=False)


# class ErrorMethod(Base):
#     __tablename__ = '_error_method'
#
#     id = Column(INTEGER,
#                 primary_key=True,
#                 server_default=text("'0'"))
#     method = Column(String(100),
#                     nullable=False,
#                     server_default=text("''"))
#
#
class PreparedSignalFile(Base):
    __tablename__ = 'prepared_signal_files'

    ID = Column(INTEGER, primary_key=True)
    _measurements_ID = Column('__measurements__ID', String(15), index=True)
    _Product_ID = Column(INTEGER, nullable=False, index=True)
    _scc_version_ID = Column(INTEGER, nullable=False)
    filename = Column(String(100), nullable=False)
