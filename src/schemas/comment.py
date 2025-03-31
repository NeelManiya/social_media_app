from pydantic import BaseModel


class CreateCommentSchema(BaseModel):
    post_id: int
    content: str


class DeleteCommentSchema(BaseModel):
    post_id: int
    comment_id: int


class CreateCommentLikeSchema(BaseModel):
    post_id: int
    comment_id: int
