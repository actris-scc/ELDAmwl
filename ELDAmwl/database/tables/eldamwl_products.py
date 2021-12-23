"""SCC database table for registering ELDAmwl results"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import Column, BIGINT
from sqlalchemy import DateTime
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import VARCHAR


class EldamwlProducts(Base):
    """content of the db table eldamwl_products

    """

    __tablename__ = 'eldamwl_products'

    ID = Column(
        BIGINT,
        primary_key=True,
    )
    measurements_id = Column(
        VARCHAR(15),
        nullable=False,
    )
    product_id = Column(
        INTEGER,
        nullable=False,
    )
    scc_version_id = Column(
        INTEGER,
        nullable=True,
    )
    InscribedAt = Column(
        DateTime,
        nullable=False,
    )
    filename = Column(
        String(100),
        nullable=False,
    )
