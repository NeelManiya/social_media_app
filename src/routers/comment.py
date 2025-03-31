from fastapi import APIRouter, HTTPException, Depends
from database.database import get_db
from src.models.user import UserModel
from src.models.post import PostModel
from src.models.comment import CommentModel, CommentLikeModel
from sqlalchemy.orm import Session
from src.utils.user import decode_token
from src.schemas.comment import (
    CreateCommentSchema,
    DeleteCommentSchema,
    CreateCommentLikeSchema,
)

comment_router = APIRouter(tags=["Comment"])


@comment_router.post("/create_comment")
def create_comment(
    token: str, comment: CreateCommentSchema, db: Session = Depends(get_db)
):
    user_detail = decode_token(token)
    id, username, email, phone_no = user_detail

    find_user = db.query(UserModel).filter(UserModel.id == id).first()

    if not find_user:
        raise HTTPException(status_code=404, detail="User not found")

    find_post = db.query(PostModel).filter(PostModel.id == comment.post_id).first()

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    new_comment = CommentModel(
        user_id=id, post_id=comment.post_id, content=comment.content
    )

    db.add(new_comment)

    find_post.comment_count = (find_post.comment_count or 0) + 1

    db.commit()
    db.refresh(new_comment)
    return {
        "message": "Comment created successfully",
        "comment_id": new_comment.id,
        "user_id": find_user.id,
        "post_id": find_post.id,
        "content": new_comment.content,
    }


@comment_router.delete("/delete_comment")
def delete_comment(comment: DeleteCommentSchema, db: Session = Depends(get_db)):

    find_post = db.query(PostModel).filter(PostModel.id == comment.post_id).first()

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    find_comment = (
        db.query(CommentModel).filter(CommentModel.id == comment.comment_id).first()
    )

    if not find_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    find_post.comment_count = (find_post.comment_count or 0) - 1

    db.delete(find_comment)
    db.commit()
    return "Comment deleted successfully"


@comment_router.post("/comment_like")
def comment_like(
    comment_like: CreateCommentLikeSchema, token: str, db: Session = Depends(get_db)
):
    user_detail = decode_token(token)
    id, username, email, phone_no = user_detail

    find_user = db.query(UserModel).filter(UserModel.id == id).first()

    if not find_user:
        raise HTTPException(status_code=404, detail="User not found")

    find_post = db.query(PostModel).filter(PostModel.id == comment_like.post_id).first()

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    find_comment = (
        db.query(CommentModel)
        .filter(CommentModel.id == comment_like.comment_id)
        .first()
    )

    if not find_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    existing_like = (
        db.query(CommentLikeModel)
        .filter(
            CommentLikeModel.user_id == id,
            CommentLikeModel.comment_id == comment_like.comment_id,
        )
        .first()
    )

    if existing_like:
        raise HTTPException(status_code=400, detail="You already liked this comment")

    new_commentlike = CommentLikeModel(
        user_id=id, post_id=comment_like.post_id, comment_id=comment_like.comment_id
    )

    db.add(new_commentlike)
    db.commit()
    db.refresh(new_commentlike)
    return {
        "message": "Liked added successfully",
        "comment_like_id": new_commentlike.id,
        "user_id": find_user.id,
        "post_id": comment_like.post_id,
        "comment_id": comment_like.comment_id,
    }


@comment_router.delete("/dislike_comment")
def dislike_comment(
    comment_id: int, commentlike_id: int, db: Session = Depends(get_db)
):

    find_comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()

    if not find_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    find_commentlike_id = (
        db.query(CommentLikeModel).filter(CommentLikeModel.id == commentlike_id).first()
    )

    if not find_commentlike_id:
        raise HTTPException(status_code=404, detail="Like not found this comment")

    db.delete(find_commentlike_id)
    db.commit()
    return "Comment dislike successfully"


# from fastapi import APIRouter, HTTPException, Depends
# from database.database import get_db
# from src.models.user import UserModel
# from src.models.post import PostModel
# from src.models.comment import CommentModel, CommentLikeModel
# from sqlalchemy.orm import Session
# from src.utils.user import decode_token
# from src.schemas.comment import (
#     CreateCommentSchema,
#     DeleteCommentSchema,
#     CreateCommentLikeSchema,
# )
# from logs.log_config import logger

# comment_router = APIRouter(tags=["Comment"])


# @comment_router.post("/create_comment")
# def create_comment(
#     token: str, comment: CreateCommentSchema, db: Session = Depends(get_db)
# ):
#     user_detail = decode_token(token)
#     id, username, email, phone_no = user_detail

#     find_user = db.query(UserModel).filter(UserModel.id == id).first()
#     if not find_user:
#         logger.warning(f"Comment creation failed: User {id} not found.")
#         raise HTTPException(status_code=404, detail="User not found")

#     find_post = db.query(PostModel).filter(PostModel.id == comment.post_id).first()
#     if not find_post:
#         logger.warning(f"Comment creation failed: Post {comment.post_id} not found.")
#         raise HTTPException(status_code=404, detail="Post not found")

#     new_comment = CommentModel(user_id=id, post_id=comment.post_id, content=comment.content)
#     db.add(new_comment)
#     find_post.comment_count = (find_post.comment_count or 0) + 1
#     db.commit()
#     db.refresh(new_comment)
#     logger.info(f"User {id} commented on Post {comment.post_id} successfully.")
#     return {
#         "message": "Comment created successfully",
#         "comment_id": new_comment.id,
#         "user_id": find_user.id,
#         "post_id": find_post.id,
#         "content": new_comment.content,
#     }


# @comment_router.delete("/delete_comment")
# def delete_comment(comment: DeleteCommentSchema, db: Session = Depends(get_db)):
#     find_post = db.query(PostModel).filter(PostModel.id == comment.post_id).first()
#     if not find_post:
#         logger.warning(f"Comment deletion failed: Post {comment.post_id} not found.")
#         raise HTTPException(status_code=404, detail="Post not found")

#     find_comment = db.query(CommentModel).filter(CommentModel.id == comment.comment_id).first()
#     if not find_comment:
#         logger.warning(f"Comment deletion failed: Comment {comment.comment_id} not found.")
#         raise HTTPException(status_code=404, detail="Comment not found")

#     find_post.comment_count = (find_post.comment_count or 0) - 1
#     db.delete(find_comment)
#     db.commit()
#     logger.info(f"Comment {comment.comment_id} deleted successfully.")
#     return "Comment deleted successfully"


# @comment_router.post("/comment_like")
# def comment_like(
#     comment_like: CreateCommentLikeSchema, token: str, db: Session = Depends(get_db)
# ):
#     user_detail = decode_token(token)
#     id, username, email, phone_no = user_detail

#     find_user = db.query(UserModel).filter(UserModel.id == id).first()
#     if not find_user:
#         logger.warning(f"Comment like failed: User {id} not found.")
#         raise HTTPException(status_code=404, detail="User not found")

#     find_post = db.query(PostModel).filter(PostModel.id == comment_like.post_id).first()
#     if not find_post:
#         logger.warning(f"Comment like failed: Post {comment_like.post_id} not found.")
#         raise HTTPException(status_code=404, detail="Post not found")

#     find_comment = db.query(CommentModel).filter(CommentModel.id == comment_like.comment_id).first()
#     if not find_comment:
#         logger.warning(f"Comment like failed: Comment {comment_like.comment_id} not found.")
#         raise HTTPException(status_code=404, detail="Comment not found")

#     existing_like = db.query(CommentLikeModel).filter(
#         CommentLikeModel.user_id == id, CommentLikeModel.comment_id == comment_like.comment_id
#     ).first()
#     if existing_like:
#         logger.warning(f"User {id} already liked Comment {comment_like.comment_id}.")
#         raise HTTPException(status_code=400, detail="You already liked this comment")

#     new_commentlike = CommentLikeModel(
#         user_id=id, post_id=comment_like.post_id, comment_id=comment_like.comment_id
#     )
#     db.add(new_commentlike)
#     db.commit()
#     db.refresh(new_commentlike)
#     logger.info(f"User {id} liked Comment {comment_like.comment_id} on Post {comment_like.post_id}.")
#     return {
#         "message": "Like added successfully",
#         "comment_like_id": new_commentlike.id,
#         "user_id": find_user.id,
#         "post_id": comment_like.post_id,
#         "comment_id": comment_like.comment_id,
#     }


# @comment_router.delete("/dislike_comment")
# def dislike_comment(comment_id: int, commentlike_id: int, db: Session = Depends(get_db)):
#     find_comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
#     if not find_comment:
#         logger.warning(f"Comment dislike failed: Comment {comment_id} not found.")
#         raise HTTPException(status_code=404, detail="Comment not found")

#     find_commentlike_id = db.query(CommentLikeModel).filter(CommentLikeModel.id == commentlike_id).first()
#     if not find_commentlike_id:
#         logger.warning(f"Comment dislike failed: Like {commentlike_id} not found.")
#         raise HTTPException(status_code=404, detail="Like not found for this comment")

#     db.delete(find_commentlike_id)
#     db.commit()
#     logger.info(f"User disliked Comment {comment_id} successfully.")
#     return "Comment disliked successfully"
