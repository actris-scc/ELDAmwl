# -*- coding: utf-8 -*-
"""Classes for db table which reflect the relation between method names and ELDAmwl class names"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import DECIMAL
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text


class EldamwlClassNames(Base):
    """content of the db table _cal_range_search_methods

    """

    __tablename__ = 'eldamwl_class_names'

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
    classname = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )

