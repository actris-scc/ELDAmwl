# -*- coding: utf-8 -*-
"""Classes for backscatter related db tables"""

from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import INTEGER
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class BscCalibrOption(Base):
    """content of the db table bsc_calibr_options

    """

    __tablename__ = 'bsc_calibr_options'

    ID = Column(INTEGER, primary_key=True)
    LowestHeight = Column(DECIMAL(10, 4),
                          nullable=False,
                          server_default=text("'0.0000'"))
    TopHeight = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))
    WindowWidth = Column(DECIMAL(10, 4),
                         nullable=False,
                         server_default=text("'0.0000'"))
    calValue = Column(DECIMAL(10, 4),
                      nullable=False,
                      server_default=text("'0.0000'"))
    _calRangeSearchMethod_ID = Column(INTEGER,
                                      nullable=False,
                                      server_default=text("'-1'"))


class ElastBackscatterOption(Base):
    """content of the db table elast_backscatter_options

    """

    __tablename__ = 'elast_backscatter_options'

    ID = Column(INTEGER, primary_key=True)
    _product_ID = Column(INTEGER,
                         nullable=False,
                         server_default=text("'-1'"))
    _elast_bsc_method_ID = Column(INTEGER,
                                  nullable=False,
                                  index=True,
                                  server_default=text("'-1'"))
    _bsc_calibr_options_ID = Column(INTEGER,
                                    nullable=False,
                                    index=True,
                                    server_default=text("'-1'"))
    _error_method_ID = Column(INTEGER,
                              nullable=False,
                              index=True,
                              server_default=text("'-1'"))
    _lr_input_method_id = Column(INTEGER,
                                 nullable=False,
                                 index=True,
                                 server_default=text("'-1'"))
    fixed_lr = Column(DECIMAL(10, 4),
                      nullable=False,
                      server_default=text("'50.0000'"))
    fixed_lr_error = Column(DECIMAL(10, 4),
                            nullable=False,
                            server_default=text("'0.0000'"))
    _iter_bsc_options_id = Column(INTEGER,
                                  nullable=False,
                                  index=True,
                                  server_default=text("'-1'"))


class RamanBackscatterOption(Base):
    """content of the db table raman_backscatter_options

    """

    __tablename__ = 'raman_backscatter_options'

    ID = Column(INTEGER, primary_key=True)
    _product_ID = Column(INTEGER,
                         nullable=False,
                         server_default=text("'-1'"))
    _ram_bsc_method_ID = Column(INTEGER,
                                nullable=False,
                                index=True,
                                server_default=text("'-1'"))
    _bsc_calibr_options_ID = Column(INTEGER,
                                    nullable=False,
                                    index=True,
                                    server_default=text("'-1'"))
    _error_method_ID = Column(INTEGER,
                              nullable=False,
                              index=True,
                              server_default=text("'-1'"))
