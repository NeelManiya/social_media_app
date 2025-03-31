from database.database import Base
from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship


class CommentModel(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id", ondelete="cascade"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    user = relationship("UserModel")
    post = relationship("PostModel")


class CommentLikeModel(Base):
    __tablename__ = "commentlike"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id", ondelete="cascade"), nullable=False)
    comment_id = Column(
        Integer, ForeignKey("comment.id", ondelete="cascade"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    user = relationship("UserModel")
    post = relationship("PostModel")
