"""SCC database table for registering ELDAmwl results"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import VARCHAR


class EldamwlProducts(Base):
    """content of the db table eldamwl_products

    """

    __tablename__ = 'eldamwl_products'

    ID = Column(
        INTEGER,
        primary_key=True,
        autoincrement=True,
    )

