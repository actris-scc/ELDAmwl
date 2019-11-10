# -*- coding: utf-8 -*-
"""Classes for lidar ratio related db tables"""

from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import DECIMAL
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class ExtBscOption(Base):
    """content of the db table ext_bsc_options

    """

    __tablename__ = 'ext_bsc_options'

    ID = Column(INTEGER, primary_key=True)
    _product_ID = Column(INTEGER,
                         nullable=False,
                         server_default=text("'-1'"))
    _extinction_options_product_ID = Column(INTEGER,
                                            nullable=False,
                                            index=True,
                                            server_default=text("'-1'"))
    _raman_backscatter_options_product_ID = Column(INTEGER,
                                                   nullable=False,
                                                   index=True,
                                                   server_default=text("'-1'"))
    _error_method_ID = Column(INTEGER,
                              nullable=False,
                              index=True,
                              server_default=text("'-1'"))
    min_BscRatio_for_LR = Column(DECIMAL(10, 4),
                            nullable=False,
                            server_default=text("'1.0000'"))
