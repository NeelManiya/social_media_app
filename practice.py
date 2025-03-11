# UPLOAD_DIR = "photos"
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# @car_router.post("/upload-photo/")
# async def upload_photo(id: str, file: UploadFile = File(...)):
#     file_location = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_location, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     get_car = db.query(Car).filter(Car.id == id).first()

#     if not get_car:
#         raise HTTPException(status_code=404, detail="Car ID incorrect")

#     get_car.car_picture = file_location

#     db.commit()
#     db.refresh(get_car)

#     return {"info": f"File '{file.filename}' saved at '{file_location}'"}

# ---------------------------------------------------------------------------------------------------------------------------------------------------------


# UPLOAD_DIR = "photos"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# post_router = APIRouter()


# @post_router.post("/create_post")
# async def create_post(
#     post: CreatePostSchema,
#     token: str,
#     file: UploadFile = File(None),  # Make file optional
#     db: Session = Depends(get_db),
# ):
#     post_detail = decode_token(token)
#     user_id, username, email, phone_no = post_detail

#     new_post = PostModel(
#         user_id=user_id,
#         title=post.title,
#         caption=post.caption,
#     )

#     # If a file is provided, upload the photo and attach the path to the post
#     if file:
#         file_location = os.path.join(UPLOAD_DIR, file.filename)
#         with open(file_location, "wb") as f:
#             shutil.copyfileobj(file.file, f)

#         new_post.image_url = file_location  # Assuming there's a column in the PostModel
#         db.add(new_post)
#         db.commit()
#         db.refresh(new_post)

#     return {
#         "message": "Post created successfully",
#         "post_id": new_post.id,
#         "title": post.title,
#         "caption": post.caption,
#         "photo_path": new_post.image_url if file else None,
#     }
