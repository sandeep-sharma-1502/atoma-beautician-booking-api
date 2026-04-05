import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, String

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
