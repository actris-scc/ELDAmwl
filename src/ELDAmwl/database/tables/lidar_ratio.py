# -*- coding: utf-8 -*-
"""Classes for lidar ratio related db tables"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import INTEGER
from sqlalchemy import text


class ExtBscOption(Base):
    """content of the db table ext_bsc_options

    """

    __tablename__ = 'ext_bsc_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
        server_default=text("'-1'"),
    )
    extinction_options_product_id = Column(
        '_extinction_options_product_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'"),
    )
    raman_backscatter_options_product_id = Column(
        '_raman_backscatter_options_product_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'"),
    )
    error_method_id = Column(
        '_error_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'"),
    )
    min_BscRatio_for_LR = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'1.0000'"),
    )
