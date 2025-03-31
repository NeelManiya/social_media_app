from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from src.schemas.post import CreatePostSchema, PostUpdateSchema
from sqlalchemy.orm import Session
from database.database import get_db
from src.models.post import PostModel
from src.utils.user import decode_token
import os, shutil


UPLOAD_DIR = "photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

post_router = APIRouter(tags=["Post"])


@post_router.post("/create_post")
async def create_post(
    token: str = Form(...),
    title: str = Form(...),
    caption: str = Form(...),
    file: UploadFile = File(None),  # Optional file
    db: Session = Depends(get_db),
):
    post_detail = decode_token(token)
    user_id, username, email, phone_no = post_detail

    new_post = PostModel(
        user_id=user_id,
        title=title,
        caption=caption,
    )

    if file:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        new_post.image_url = file_location
        db.add(new_post)
        db.commit()
        db.refresh(new_post)

    return {
        "message": "Post created successfully",
        "post_id": new_post.id,
        "user_id": new_post.user_id,
        "title": new_post.title,
        "caption": new_post.caption,
        "photo_path": new_post.image_url if file else None,
    }


@post_router.get("/get_post/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    find_post = (
        db.query(PostModel)
        .filter(PostModel.id == id, PostModel.is_deleted == False)
        .first()
    )

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post_id": find_post.id,
        "user_id": find_post.user_id,
        "title": find_post.title,
        "caption": find_post.caption,
    }


@post_router.patch("/update")
def update_post(post: PostUpdateSchema, id: int, db: Session = Depends(get_db)):
    find_user = db.query(PostModel).filter(PostModel.id == id).first()

    if not find_user:
        raise HTTPException(status_code=404, detail="Post not found")

    find_user.title = post.title
    find_user.caption = post.caption

    db.commit()
    db.refresh(find_user)
    return {
        "message": "Post updated successfully",
        "title": post.title,
        "caption": post.caption,
        "post_id": find_user.id,
    }


@post_router.delete("/delete_post")
def delete_post(id: int, db: Session = Depends(get_db)):

    find_post = (
        db.query(PostModel)
        .filter(PostModel.id == id, PostModel.is_deleted == False)
        .first()
    )

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    find_post.is_deleted = True

    db.delete(find_post)
    db.commit()

    return {"message": "post deleted successfully"}


@post_router.get("/get_All_post")
def get_all_post(db: Session = Depends(get_db)):
    find_post = db.query(PostModel).all()

    return find_post


# from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
# from src.schemas.post import CreatePostSchema, PostUpdateSchema
# from sqlalchemy.orm import Session
# from database.database import get_db
# from src.models.post import PostModel
# from src.utils.user import decode_token
# import os, shutil
# from logs.log_config import logger

# UPLOAD_DIR = "photos"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# post_router = APIRouter(tags=["Post"])

# @post_router.post("/create_post")
# async def create_post(
#     token: str = Form(...),
#     title: str = Form(...),
#     caption: str = Form(...),
#     file: UploadFile = File(None),  # Optional file
#     db: Session = Depends(get_db),
# ):
#     post_detail = decode_token(token)
#     user_id, username, email, phone_no = post_detail

#     new_post = PostModel(
#         user_id=user_id,
#         title=title,
#         caption=caption,
#     )

#     if file:
#         file_location = os.path.join(UPLOAD_DIR, file.filename)
#         with open(file_location, "wb") as f:
#             shutil.copyfileobj(file.file, f)

#         new_post.image_url = file_location
#         db.add(new_post)
#         db.commit()
#         db.refresh(new_post)

#     logger.info(f"Post created successfully: {new_post.id}")

#     return {
#         "message": "Post created successfully",
#         "post_id": new_post.id,
#         "user_id": new_post.user_id,
#         "title": new_post.title,
#         "caption": new_post.caption,
#         "photo_path": new_post.image_url if file else None,
#     }

# @post_router.get("/get_post/{id}")
# def get_post(id: int, db: Session = Depends(get_db)):
#     find_post = (
#         db.query(PostModel)
#         .filter(PostModel.id == id, PostModel.is_deleted == False)
#         .first()
#     )

#     if not find_post:
#         logger.warning(f"Post not found: {id}")
#         raise HTTPException(status_code=404, detail="Post not found")

#     logger.info(f"Post retrieved successfully: {id}")

#     return {
#         "post_id": find_post.id,
#         "user_id": find_post.user_id,
#         "title": find_post.title,
#         "caption": find_post.caption,
#     }

# @post_router.patch("/update")
# def update_post(post: PostUpdateSchema, id: int, db: Session = Depends(get_db)):
#     find_user = db.query(PostModel).filter(PostModel.id == id).first()

#     if not find_user:
#         logger.warning(f"Post not found for update: {id}")
#         raise HTTPException(status_code=404, detail="Post not found")

#     find_user.title = post.title
#     find_user.caption = post.caption

#     db.commit()
#     db.refresh(find_user)

#     logger.info(f"Post updated successfully: {id}")

#     return {
#         "message": "Post updated successfully",
#         "title": post.title,
#         "caption": post.caption,
#         "post_id": find_user.id,
#     }

# @post_router.delete("/delete_post")
# def delete_post(id: int, db: Session = Depends(get_db)):
#     find_post = (
#         db.query(PostModel)
#         .filter(PostModel.id == id, PostModel.is_deleted == False)
#         .first()
#     )

#     if not find_post:
#         logger.warning(f"Post not found for deletion: {id}")
#         raise HTTPException(status_code=404, detail="Post not found")

#     find_post.is_deleted = True

#     db.delete(find_post)
#     db.commit()

#     logger.info(f"Post deleted successfully: {id}")

#     return {"message": "Post deleted successfully"}

# @post_router.get("/get_All_post")
# def get_all_post(db: Session = Depends(get_db)):
#     find_post = db.query(PostModel).all()

#     logger.info("All posts retrieved successfully")

#     return find_post
