# -*- coding: utf-8 -*-
"""Classes for measurement system-product related db tables"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import Float
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text


class SystemProduct(Base):
    __tablename__ = 'system_product'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    system_id = Column(
        '_system_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    product_id = Column(
        '_Product_ID',
        INTEGER,
        nullable=False,
        index=True,
    )


class MWLproductProduct(Base):
    __tablename__ = 'mwlproduct_product'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    mwl_product_id = Column(
        '_mwl_product_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    product_id = Column(
        '_Product_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    create_with_hr = Column(
        INTEGER,
        nullable=False,
        index=False,
    )
    create_with_lr = Column(
        INTEGER,
        nullable=False,
        index=False,
    )


class Products(Base):
    __tablename__ = 'products'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    usecase_id = Column(
        '_usecase_ID',
        INTEGER,
    )
    prod_type_id = Column(
        '_prod_type_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    hoi_stations_id = Column(
        '__hoi_stations__ID',
        CHAR(3),
    )
    hirelpp_product_option_id = Column(
        '_hirelpp_product_option_ID',
        INTEGER,
    )


class ProductTypes(Base):
    __tablename__ = '_product_types'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_type = Column(
        CHAR(100),
        nullable=False,
    )
    # Changed to Nullable for csv import to work.
    description = Column(
        CHAR(100),
        nullable=True,
    )
    nc_file_id = Column(
        CHAR(1),
        nullable=False,
    )
    processor_ID = Column(
        INTEGER,
        nullable=False,
    )
    # Changed to Nullable for csv import to work.
    is_mwl_only_product = Column(
        INTEGER,
        nullable=True,
    )
    # Changed to Nullable for csv import to work.
    is_in_mwl_products = Column(
        INTEGER,
        nullable=True,
    )
    # Changed to Nullable for csv import to work.
    is_basic_product = Column(
        INTEGER,
        nullable=True,
    )


class PreProcOptions(Base):
    __tablename__ = 'preproc_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
    )
    min_height = Column(
        DECIMAL(10, 4),
        nullable=False,
    )
    max_height = Column(
        DECIMAL(10, 4),
        nullable=False,
    )
    preprocessing_integration_time = Column(
        INTEGER,
        nullable=False,
    )
    preprocessing_vertical_resolution = Column(
        DECIMAL(10, 4),
        nullable=False,
    )
    interpolation_id = Column(
        INTEGER,
        nullable=False,
    )


class SmoothOptions(Base):
    __tablename__ = 'smooth_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
    )
    lowrange_error_threshold_id = Column(
        '_lowrange_error_threshold_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    highrange_error_threshold_id = Column(
        '_highrange_error_threshold_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    detection_limit = Column(
        DECIMAL(11, 11),
        nullable=False,
    )
    transition_zone_from = Column(
        DECIMAL(10, 4),
        nullable=True,
    )
    transition_zone_to = Column(
        DECIMAL(10, 4),
        nullable=True,
    )
    lowres_lowrange_vertical_resolution = Column(
        DECIMAL(10, 4),
        nullable=True,
    )
    lowres_highrange_vertical_resolution = Column(
        DECIMAL(10, 4),
        nullable=True,
    )
    highres_lowrange_vertical_resolution = Column(
        DECIMAL(10, 4),
        nullable=True,
    )
    highres_highrange_vertical_resolution = Column(
        DECIMAL(10, 4),
        nullable=True,
    )
    lowres_integration_time = Column(
        'lowres_lowrange_integration_time',
        INTEGER,
        nullable=True,
    )
    highres_integration_time = Column(
        'highres_lowrange_integration_time',
        INTEGER,
        nullable=True,
    )
    smooth_type_id = Column(
        '_smooth_type',
        INTEGER,
        nullable=False,
    )


class ErrorThresholds(Base):
    __tablename__ = '_error_thresholds'

    ID = Column(
        'Id',
        INTEGER,
        primary_key=True,
    )
    value = Column(
        Float,
        nullable=False,
    )
    name = Column(
        String(100),
        nullable=False,
    )


class SmoothTypes(Base):
    __tablename__ = '_smooth_types'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    smooth_type = Column(
        String(50),
        nullable=False,
    )


class SmoothMethod(Base):
    """content of the db table _smooth_methods

    contains smooth methods (e.g. sliding average or Savitzky-Golay)
    and Python classnames for the smoothing and the corresponding calculation
    of effective and used bin resolution

    """

    __tablename__ = '_smooth_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text("'0'"),
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )
    method_for_getting_used_binres = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )
    method_for_getting_effective_binres = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )


class PreparedSignalFile(Base):
    __tablename__ = 'prepared_signal_files'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    measurements_id = Column(
        '__measurements__ID',
        String(15),
        index=True,
    )
    product_id = Column(
        '_Product_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    scc_version_id = Column(
        '_scc_version_ID',
        INTEGER,
        nullable=False,
    )
    filename = Column(
        String(100),
        nullable=False,
    )


class MCOption(Base):
    __tablename__ = 'mc_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    iteration_count = Column(
        INTEGER,
        nullable=False,
    )
