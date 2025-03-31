from pydantic import BaseModel


class CreatePostSchema(BaseModel):
    user_id: str
    title: str
    caption: str


class PostUpdateSchema(BaseModel):
    title: str
    caption: str
