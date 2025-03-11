from pydantic import BaseModel


class FollowUser(BaseModel):
    following_id: int
    # follower_id: int


class UnfollowUser(BaseModel):
    following_id: int
    # follower_id: int
