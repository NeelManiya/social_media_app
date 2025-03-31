from database.database import SessionLocal, get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.user import UserModel
from src.utils.user import decode_token
from src.models.post import PostModel
from src.models.like import LikeModel

like_router = APIRouter(tags=["Like"])


@like_router.post("/create_like")
def create_like(token: str, post_id: int, db: Session = Depends(get_db)):
    user_detail = decode_token(token)
    id, username, email, phone_no = user_detail
    # breakpoint()
    find_user = db.query(UserModel).filter(UserModel.id == id).first()

    if not find_user:
        raise HTTPException(status_code=404, detail="User not found")

    find_post = db.query(PostModel).filter(PostModel.id == post_id).first()

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = (
        db.query(LikeModel)
        .filter(LikeModel.user_id == id, LikeModel.post_id == post_id)
        .first()
    )

    if existing_like:
        raise HTTPException(status_code=400, detail="You already like this post")

    new_like = LikeModel(
        user_id=id,
        post_id=post_id,
    )

    db.add(new_like)

    find_post.like_count = (find_post.like_count or 0) + 1

    db.commit()
    db.refresh(new_like)
    return {
        "message": "Like created successfully",
        "like_id": new_like.id,
        "user_id": find_user.id,
        "post_id": find_post.id,
    }


@like_router.delete("/dislike")
def dislike(like_id: int, post_id: int, db: Session = Depends(get_db)):

    find_post = db.query(PostModel).filter(PostModel.id == post_id).first()

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    find_like = db.query(LikeModel).filter(LikeModel.id == like_id).first()

    if not find_like:
        raise HTTPException(status_code=404, detail="Like not found this post")

    find_post.like_count = (find_post.like_count or 0) - 1

    db.delete(find_like)
    db.commit()
    return {
        "message": "dislike successfully",
    }


# from database.database import SessionLocal, get_db
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from src.models.user import UserModel
# from src.utils.user import decode_token
# from src.models.post import PostModel
# from src.models.like import LikeModel
# from logs.log_config import logger

# like_router = APIRouter(tags=["Like"])


# @like_router.post("/create_like")
# def create_like(token: str, post_id: int, db: Session = Depends(get_db)):
#     user_detail = decode_token(token)
#     id, username, email, phone_no = user_detail

#     find_user = db.query(UserModel).filter(UserModel.id == id).first()
#     if not find_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     find_post = db.query(PostModel).filter(PostModel.id == post_id).first()
#     if not find_post:
#         raise HTTPException(status_code=404, detail="Post not found")

#     existing_like = (
#         db.query(LikeModel)
#         .filter(LikeModel.user_id == id, LikeModel.post_id == post_id)
#         .first()
#     )

#     if existing_like:
#         raise HTTPException(status_code=400, detail="You already like this post")

#     new_like = LikeModel(
#         user_id=id,
#         post_id=post_id,
#     )

#     db.add(new_like)
#     find_post.like_count = (find_post.like_count or 0) + 1
#     db.commit()
#     db.refresh(new_like)

#     logger.info(f"User {username} liked post {post_id}")

#     return {
#         "message": "Like created successfully",
#         "like_id": new_like.id,
#         "user_id": find_user.id,
#         "post_id": find_post.id,
#     }


# @like_router.delete("/dislike")
# def dislike(like_id: int, post_id: int, db: Session = Depends(get_db)):
#     find_post = db.query(PostModel).filter(PostModel.id == post_id).first()
#     if not find_post:
#         raise HTTPException(status_code=404, detail="Post not found")

#     find_like = db.query(LikeModel).filter(LikeModel.id == like_id).first()
#     if not find_like:
#         raise HTTPException(status_code=404, detail="Like not found for this post")

#     find_post.like_count = (find_post.like_count or 0) - 1
#     db.delete(find_like)
#     db.commit()

#     logger.info(f"Like {like_id} removed from post {post_id}")

#     return {"message": "Dislike successfully"}
