# -*- coding: utf-8 -*-
"""Classes for angstroem exponent related db tables"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import INTEGER
from sqlalchemy import text


class AngstroemExpOption(Base):
    """content of the db table angstroem_exp_options

    """

    __tablename__ = 'angstroem_exp_options'

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
    lambda1_product_id = Column(
        '_lambda1_product_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'"),
    )
    lambda2_product_id = Column(
        '_lambda2_product_ID',
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
    min_BscRatio_for_AE = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text("'1.0000'"),
    )
