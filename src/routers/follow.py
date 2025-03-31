from fastapi import APIRouter, Depends, HTTPException
from src.schemas.follow import FollowUser, UnfollowUser
from database.database import get_db
from sqlalchemy.orm import Session
from src.models.user import UserModel
from src.models.follow import FollowModel
from src.utils.user import decode_token


follow_router = APIRouter(tags=["Folow"])


@follow_router.post("/follow")
def follow_user(follow: FollowUser, token: str, db: Session = Depends(get_db)):
    user_detail = decode_token(token)
    id, name, email, phone_no = user_detail

    find_user = db.query(UserModel).filter(UserModel.id == follow.following_id).first()

    if not find_user:
        raise HTTPException(status_code=404, detail="User not found")

    follow_user = FollowModel(following_id=follow.following_id, followers_id=id)

    follow_user.follow = True
    follow_user.unfollow = False

    db.add(follow_user)
    db.commit()
    db.refresh(follow_user)
    return {"message": "User follow"}


@follow_router.delete("/unfollow")
def unfollow(follow: UnfollowUser, token: str, db: Session = Depends(get_db)):
    user_detail = decode_token(token)
    id, name, email, phone_no = user_detail

    unfollow_user = (
        db.query(FollowModel)
        .filter(
            FollowModel.following_id == follow.following_id,
            FollowModel.followers_id == id,
        )
        .first()
    )

    if not unfollow_user:
        raise HTTPException(status_code=404, detail="User not found")

    unfollow_user.unfollow = True
    unfollow_user.follow = False

    db.delete(unfollow_user)
    db.commit()
    return {"message": "User unfollowed successfully"}


# from fastapi import APIRouter, Depends, HTTPException
# from src.schemas.follow import FollowUser, UnfollowUser
# from database.database import get_db
# from sqlalchemy.orm import Session
# from src.models.user import UserModel
# from src.models.follow import FollowModel
# from src.utils.user import decode_token
# from logs.log_config import logger


# follow_router = APIRouter(tags=["Follow"])


# @follow_router.post("/follow")
# def follow_user(follow: FollowUser, token: str, db: Session = Depends(get_db)):
#     user_detail = decode_token(token)
#     id, name, email, phone_no = user_detail

#     find_user = db.query(UserModel).filter(UserModel.id == follow.following_id).first()

#     if not find_user:
#         logger.warning(f"Follow attempt failed: User {follow.following_id} not found.")
#         raise HTTPException(status_code=404, detail="User not found")

#     follow_user = FollowModel(following_id=follow.following_id, followers_id=id)

#     follow_user.follow = True
#     follow_user.unfollow = False

#     db.add(follow_user)
#     db.commit()
#     db.refresh(follow_user)
#     logger.info(f"User {id} followed User {follow.following_id} successfully.")
#     return {"message": "User follow"}


# @follow_router.delete("/unfollow")
# def unfollow(follow: UnfollowUser, token: str, db: Session = Depends(get_db)):
#     user_detail = decode_token(token)
#     id, name, email, phone_no = user_detail

#     unfollow_user = (
#         db.query(FollowModel)
#         .filter(
#             FollowModel.following_id == follow.following_id,
#             FollowModel.followers_id == id,
#         )
#         .first()
#     )

#     if not unfollow_user:
#         logger.warning(f"Unfollow attempt failed: User {follow.following_id} not found.")
#         raise HTTPException(status_code=404, detail="User not found")

#     unfollow_user.unfollow = True
#     unfollow_user.follow = False

#     db.delete(unfollow_user)
#     db.commit()
#     logger.info(f"User {id} unfollowed User {follow.following_id} successfully.")
#     return {"message": "User unfollowed successfully"}
