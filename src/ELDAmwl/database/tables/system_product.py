from sqlalchemy import Boolean, Index, INTEGER, CHAR, DateTime, Table, text, VARCHAR
from sqlalchemy import Column
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


