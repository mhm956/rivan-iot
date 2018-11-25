import datetime
import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean

Base = declarative_base()


class ErrorCodes(Base):
    __tablename__ = 'error_codes'

    id = Column(Integer, primary_key=True)
    active_state = Column(Boolean, default=True)
    network_addr = Column(String)
    error_code = Column(Integer)
    description = Column(String)
    created_dts = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<ErrorCodes(network_addr='%s', error_code='%d', description='%s')>" % \
               (self.network_addr, self.error_code, self.description)


def create_table(engine):
    Base.metadata.create_all(bind=engine)


def serialize_row(row_object):
    """Turn a row from ErrorCodes into a JSON string"""
    temp_log = row_object.__dict__
    temp_log.pop('_sa_instance_state', None)
    temp_log['created_dts'] = str(temp_log['created_dts'])
    return json.dumps(temp_log)
