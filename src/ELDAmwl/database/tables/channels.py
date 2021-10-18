# -*- coding: utf-8 -*-
"""Classes for measurement system-product related db tables"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text


class ProductChannels(Base):
    __tablename__ = 'product_channels'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    prod_id = Column(
        '_prod_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    channel_id = Column(
        '_channel_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    signal_type_id = Column(
        '_signal_type_id',
        INTEGER,
        nullable=False,
    )


class Channels(Base):
    __tablename__ = 'hoi_channels'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    string_ID = Column(
        String(20),
        nullable=True,
        server_default=text("''"),
    )
    name = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )
    telescope_id = Column(
        '_telescope_ID',
        INTEGER,
        nullable=False,
        server_default=text("'0'"),
    )
    laser_id = Column(
        '_laser_ID',
        INTEGER,
        nullable=False,
        server_default=text("'0'"),
    )
    scat_mechanism_id = Column(
        '_scat_mechanism_ID',
        INTEGER,
        nullable=False,
        server_default=text("'0'"),
    )
    IF_center = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'"),
    )
    IF_FWHM = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'"),
    )
    emission_wavelength = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'"),
    )
    FOV = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'"),
    )
    raw_range_resolution = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'"),
    )
    dead_time_corr_type_id = Column(
        '_dead_time_corr_type_id',
        INTEGER,
        nullable=False,
        server_default=text("'0'"),
    )
    dead_time = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'"),
    )
    trigger_delay = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'0.0000'"),
    )
    trigger_delay_interp_id = Column(
        INTEGER,
        nullable=False,
    )
    background_mode_id = Column(
        '_background_mode_id',
        INTEGER,
        nullable=False,
        server_default=text("'0'"),
    )
    signal_type_id = Column(
        '_signal_type_id',
        INTEGER,
        nullable=False,
        server_default=text("'0'"),
    )
    detection_mode_id = Column(
        '_detection_mode_ID',
        String(5),
        nullable=False,
        server_default=text("'0'"),
    )
