#COMMIT TO MASTER ONLY

from sqlalchemy import Column, Integer, VARCHAR, String, ForeignKey, Text, JSON, DateTime, Boolean
from database.db import Base
from datetime import datetime, timedelta

from sqlalchemy.orm import relationship


class Doctor(Base):
    __tablename__ = "doctor"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    title = Column(String(255))
    mobile = Column(VARCHAR(20), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    is_available = Column(Boolean, default=False)

