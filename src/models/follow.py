from database.database import Base
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class FollowModel(Base):
    __tablename__ = "follow"
    id = Column(Integer, primary_key=True, nullable=False)
    following_id = Column(
        Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False
    )
    # user = relationship("UserModel")
    followers_id = Column(
        Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False
    )
    # user = relationship("UserModel")
    follow = Column(Boolean, default=False)
    unfollow = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
