from sqlalchemy import Boolean, Index, INTEGER, CHAR, DateTime, Table, text, VARCHAR
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class SystemProduct(Base):
    __tablename__ = 'system_product'

    ID = Column(INTEGER, primary_key=True)
    _system_ID = Column(INTEGER, nullable=False, index=True)
    _Product_ID = Column(INTEGER, nullable=False, index=True)
