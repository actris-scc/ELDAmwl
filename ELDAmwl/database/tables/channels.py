# -*- coding: utf-8 -*-
"""Classes for measurement system-product related db tables"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import FLOAT
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


class Telescopes(Base):
    __tablename__ = 'hoi_telescopes'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    type = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )
    diameter = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0'"),
    )
    focal_length = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0'"),
    )
    full_overlap_height_m = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0'"),
    )
    # manufacturer = Column(
    #     String(100),
    #     nullable=True,
    # )
    # model = Column(
    #     String(100),
    #     nullable=True,
    # )
    # obscuration_diameter = Column(
    #     FLOAT,
    #     nullable=True,
    # )
    # field_of_view = Column(
    #     FLOAT,
    #     nullable=True,
    # )
    # field_stop_type = Column(
    #     String(45),
    #     nullable=True,
    # )
    # field_stop_size = Column(
    #     FLOAT,
    #     nullable=True,
    # )
    # optical_fiber_num_aperture = Column(
    #     FLOAT,
    #     nullable=True,
    # )
    # optical_fiber_manufacturer = Column(
    #     String(100),
    #     nullable=True,
    # )
    # optical_fiber_type = Column(
    #     String(100),
    #     nullable=True,
    # )
    # collimation_focal_length = Column(
    #     FLOAT,
    #     nullable=True,
    # )
    # entry_update_date = Column(
    #     DateTime,
    #     nullable=False,
    # )
    # collimation_type = Column(
    #     String(100),
    #     nullable=True,
    # )
    # collimation_model = Column(
    #     String(100),
    #     nullable=True,
    # )
    station_id = Column(
        '__hoi_stations__ID',
        INTEGER,
        nullable=True,
    )
    locked = Column(
        INTEGER,
        nullable=False,
        server_default=text("'0'"),
    )
