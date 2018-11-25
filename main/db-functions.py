from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Integer, String

Base = declarative_base()


class ErrorCodes(Base):
    __tablename__ = 'error_codes'

    id = Column(Integer, primary_key=True)
    network_addr = Column(String)
    error_code = Column(Integer)
    description = Column(String)
