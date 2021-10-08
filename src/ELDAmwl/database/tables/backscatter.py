# -*- coding: utf-8 -*-
"""Classes for backscatter related db tables"""

from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import DateTime
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BscCalibrOption(Base):
    """content of the db table bsc_calibr_options

    """

    __tablename__ = 'bsc_calibr_options'

    ID = Column(
        INTEGER, primary_key=True
    )
    LowestHeight = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'")
    )
    TopHeight = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'")
    )
    WindowWidth = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'")
    )
    calValue = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'")
    )
    _calRangeSearchMethod_ID = Column(
        INTEGER,
        nullable=False,
        server_default=text("'-1'")
    )


class BscCalibrMethod(Base):
    """content of the db table _cal_range_search_methods

    """

    __tablename__ = '_cal_range_search_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text("'0'")
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text("''")
    )
    python_classname = Column(
        String(100),
        nullable=False,
        server_default=text("''")
    )


class BscMethod(Base):
    """content of the db table _bsc_methods

    """

    __tablename__ = '_bsc_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text("'0'")
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text("''")
    )


class RamanBscMethod(Base):
    """content of the db table _ram_bsc_methods

    """

    __tablename__ = '_ram_bsc_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text("'0'")
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text("''")
    )
    python_classname = Column(
        String(100),
        nullable=False,
        server_default=text("''")
    )


class ElastBscMethod(Base):
    """content of the db table _elast_bsc_methods

    """

    __tablename__ = '_elast_bsc_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text("'0'")
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text("''")
    )
    python_classname = Column(
        String(100),
        nullable=False,
        server_default=text("''")
    )


class RamanBackscatterOption(Base):
    """content of the db table raman_backscatter_options

    """

    __tablename__ = 'raman_backscatter_options'

    ID = Column(
        INTEGER,
        primary_key=True
    )
    _product_ID = Column(
        INTEGER,
        nullable=False,
        server_default=text("'-1'")
    )
    _ram_bsc_method_ID = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    _bsc_calibr_options_ID = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    _error_method_ID = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    _smooth_method_ID = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'0'")
    )


class ElastBackscatterOption(Base):
    """content of the db table elast_backscatter_options

    """

    __tablename__ = 'elast_backscatter_options'

    ID = Column(
        INTEGER,
        primary_key=True
    )
    _product_ID = Column(
        INTEGER,
        nullable=False,
        server_default=text("'-1'")
    )
    _elast_bsc_method_ID = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    _bsc_calibr_options_ID = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    _error_method_ID = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    _lr_input_method_id = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    fixed_lr = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'50.0000'")
    )
    fixed_lr_error = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'")
    )
    _iter_bsc_options_id = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    _smooth_method_ID = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'0'")
    )


class IterBackscatterOption(Base):
    """content of the db table iter_backscatter_options

    """

    __tablename__ = 'iter_backscatter_options'

    ID = Column(
        INTEGER,
        primary_key=True
    )
    iter_conv_crit = Column(
        DECIMAL,
        nullable=False,
        index=True,
        server_default=text("'0.0100'")
    )
    _ram_bsc_method_id = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'")
    )
    max_iteration_count = Column(
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'10'")
    )


class LRFile(Base):
    """content of the db table lidarratio_files

    """

    __tablename__ = 'lidarratio_files'

    ID = Column(
        INTEGER,
        primary_key=True
    )
    # Rule is: If a column has two underscores reduce to one
    _hoi_stations_ID = Column(
        '__hoi_stations__ID',
        CHAR(3)
    )
    start = Column(
        DateTime
    )
    stop = Column(
        DateTime
    )
    filename = Column(
        String(100),
        nullable=False,
        server_default=text("''")
    )
    _interpolation_id = Column(
        INTEGER
    )
    submission_date = Column(
        DateTime
    )
    status = Column(
        String(20),
        nullable=False
    )
