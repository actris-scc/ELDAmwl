# -*- coding: utf-8 -*-
"""Classes for measurement system-product related db tables"""

from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import Float
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ProductChannels(Base):
    __tablename__ = 'product_channels'

    ID = Column(INTEGER, primary_key=True)
    _prod_ID = Column(INTEGER, nullable=False, index=True)
    _channel_ID = Column(INTEGER, nullable=False, index=True)


class Channels(Base):
    __tablename__ = 'hoi_channels'

    ID = Column(INTEGER, primary_key=True)
    string_ID = Column(String(20),
                    nullable=True,
                    server_default=text("''"))
    name = Column(String(100),
                    nullable=False,
                    server_default=text("''"))
    _telescope_ID = Column(INTEGER, nullable=False,
                    server_default=text("0"))
    _laser_ID = Column(INTEGER, nullable=False,
                    server_default=text("0"))
    _scat_mechanism_ID = Column(INTEGER, nullable=False,
                    server_default=text("0"))
    IF_center = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))
    IF_FWHM = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))
    emission_wavelength = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))
    FOV = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))
    raw_range_resolution = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))
    _dead_time_corr_type_id = Column(INTEGER, nullable=False,
                    server_default=text("0"))
    dead_time = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))
    trigger_delay = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))
    trigger_delay_interp_id = Column(INTEGER, nullable=False)
    _background_mode_id = Column(INTEGER, nullable=False,
                    server_default=text("0"))
    _signal_type_id = Column(INTEGER, nullable=False,
                    server_default=text("0"))
    _detection_mode_ID = Column(String(5),
                    nullable=False,
                    server_default=text("0"))

