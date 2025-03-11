from database.database import Base
from sqlalchemy import String, Column, Integer, Boolean, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship


class PostModel(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(100), nullable=False)
    caption = Column(String(300))
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    is_deleted = Column(Boolean, default=False)
    image_url = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    user = relationship("UserModel")
