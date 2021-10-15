# -*- coding: utf-8 -*-
"""Classes for backscatter related db tables"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import DECIMAL
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text


class BscCalibrOption(Base):
    """content of the db table bsc_calibr_options

    """

    __tablename__ = 'bsc_calibr_options'

    ID = Column(
        INTEGER, primary_key=True,
    )
    LowestHeight = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text('0.0000'),
    )
    TopHeight = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text('0.0000'),
    )
    WindowWidth = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text('0.0000'),
    )
    calValue = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text('0.0000'),
    )
    calRangeSearchMethod_ID = Column(
        '_calRangeSearchMethod_ID',
        INTEGER,
        nullable=False,
        server_default=text('-1'),
    )


class BscCalibrMethod(Base):
    """content of the db table _cal_range_search_methods

    """

    __tablename__ = '_cal_range_search_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text('0'),
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )
    python_classname = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )


class BscMethod(Base):
    """content of the db table _bsc_methods

    """

    __tablename__ = '_bsc_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text('0'),
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )


class RamanBscMethod(Base):
    """content of the db table _ram_bsc_methods

    """

    __tablename__ = '_ram_bsc_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text('0'),
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )
    python_classname = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )


class ElastBscMethod(Base):
    """content of the db table _elast_bsc_methods

    """

    __tablename__ = '_elast_bsc_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text('0'),
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )
    python_classname = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )


class RamanBackscatterOption(Base):
    """content of the db table raman_backscatter_options

    """

    __tablename__ = 'raman_backscatter_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    # Todo Ina: Change to non underscore names.
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
        server_default=text('-1'),
    )
    ram_bsc_method_id = Column(
        '_ram_bsc_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    bsc_calibr_options_id = Column(
        '_bsc_calibr_options_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    error_method_id = Column(
        '_error_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    smooth_method_id = Column(
        '_smooth_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('0'),
    )


class ElastBackscatterOption(Base):
    """content of the db table elast_backscatter_options

    """

    __tablename__ = 'elast_backscatter_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
        server_default=text('-1'),
    )
    elast_bsc_method_id = Column(
        '_elast_bsc_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    bsc_calibr_options_id = Column(
        '_bsc_calibr_options_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    error_method_id = Column(
        '_error_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    lr_input_method_id = Column(
        '_lr_input_method_id',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    fixed_lr = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text('50.0000'),
    )
    fixed_lr_error = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text('0.0000'),
    )
    iter_bsc_options_id = Column(
        '_iter_bsc_options_id',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    smooth_method_id = Column(
        '_smooth_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('0'),
    )


class IterBackscatterOption(Base):
    """content of the db table iter_backscatter_options

    """

    __tablename__ = 'iter_backscatter_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    iter_conv_crit = Column(
        DECIMAL,
        nullable=False,
        index=True,
        server_default=text('0.0100'),
    )
    ram_bsc_method_id = Column(
        '_ram_bsc_method_id',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    max_iteration_count = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('10'),
    )


class LRFile(Base):
    """content of the db table lidarratio_files

    """

    __tablename__ = 'lidarratio_files'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    # Rule is: If a column has two underscores reduce to one
    hoi_stations_id = Column(
        '__hoi_stations__ID',
        CHAR(3),
    )
    start = Column(
        DateTime,
    )
    stop = Column(
        DateTime,
    )
    filename = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )
    interpolation_id = Column(
        '_interpolation_id',
        INTEGER,
    )
    submission_date = Column(
        DateTime,
    )
    status = Column(
        String(20),
        nullable=False,
    )
