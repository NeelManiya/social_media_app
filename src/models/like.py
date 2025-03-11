from database.database import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from datetime import datetime
from sqlalchemy.orm import relationship


class LikeModel(Base):
    __tablename__ = "like"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id", ondelete="cascade"), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    user = relationship("UserModel")
    post = relationship("PostModel")
