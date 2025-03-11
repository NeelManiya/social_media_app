from database.database import Base
from sqlalchemy import String, Column, Integer, Boolean, DateTime, ForeignKey, BIGINT
from datetime import datetime
from sqlalchemy.orm import relationship


class UserModel(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String(15), nullable=False)
    email = Column(String(30), nullable=False)
    phone_no = Column(BIGINT, nullable=False)
    password = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=False), default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


class OTPModel(Base):
    __tablename__ = "otp"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
    email = Column(String(50), nullable=False)
    otp = Column(String(6), nullable=False)
    created_at = Column(DateTime(timezone=False), default=datetime.now, nullable=False)
