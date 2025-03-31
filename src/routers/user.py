from fastapi import APIRouter, Depends, HTTPException
from database.database import get_db
from src.schemas.user import (
    UserCreateSchema,
    UserUpdateSchema,
    ResetPasswordSchema,
    ForgetPasswordSchema,
)
from src.models.user import UserModel, OTPModel
import uuid
from src.utils.user import pwd_context, Gen_OTP, pass_checker, get_token, decode_token
from sqlalchemy.orm import Session
from pydantic import validate_email
from logs.log_config import logger


user_router = APIRouter(tags=["User"])


@user_router.post("/signup")
def create_new_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    try:
        validate_email(user.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Email already exist!")

    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = UserModel(
        username=user.username,
        email=user.email,
        phone_no=user.phone_no,
        password=pwd_context.hash(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user signed up: {user.email}")
    return {
        "message": "User Signup successfully, Now go for verification",
        "user_id": new_user.id,
        "email": new_user.email,
        "username": new_user.username,
        "phone_no": new_user.phone_no,
    }


@user_router.post("/generate_OTP")
def Generate_OTP(email: str):
    Gen_OTP(email)
    logger.info(f"OTP send successfully: {email}")
    return "OTP generated successfully now go for verification"


@user_router.get("/verify_otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    find_user_with_email = (
        db.query(UserModel)
        .filter(
            UserModel.email == email,
            UserModel.is_active == True,
            UserModel.is_verified == False,
            UserModel.is_deleted == False,
        )
        .first()
    )

    if not find_user_with_email:
        raise HTTPException(status_code=400, detail="User not found")

    find_otp = (
        db.query(OTPModel).filter(OTPModel.email == email, OTPModel.otp == otp).first()
    )

    if not find_otp:
        raise HTTPException(status_code=400, detail="OTP not found")

    find_user_with_email.is_verified = True
    db.commit()
    db.refresh(find_user_with_email)
    logger.info(f"User verify successfully: {find_user_with_email.email}")
    return "OTP verified successfully"


@user_router.get("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    find_user = (
        db.query(UserModel).filter(
            UserModel.email == email,
            UserModel.is_active == True,
            UserModel.is_deleted == False,
            UserModel.is_verified == True,
        )
    ).first()

    if not find_user:
        raise HTTPException(status_code=400, detail="User not found")

    pass_checker(password, find_user.password)

    access_token = get_token(
        find_user.id, find_user.username, find_user.email, find_user.phone_no
    )

    logger.info(f"User Login: {find_user.email}")

    return {
        "message": "User login successfully",
        "id": find_user.id,
        "email": find_user.email,
        "username": find_user.username,
        "Token type": "Bearer",
        "access token": access_token,
    }


@user_router.patch("/update_user")
def update_user(token: str, user: UserUpdateSchema, db: Session = Depends(get_db)):
    user_detail = decode_token(token)
    id, username, email, phone_no = user_detail
    find_user = (
        db.query(UserModel)
        .filter(
            UserModel.id == id,
            UserModel.is_active == True,
            UserModel.is_verified == True,
            UserModel.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        raise HTTPException(status_code=404, detail="User not found")

    find_user.username = user.username
    find_user.email = user.email
    find_user.phone_no = user.phone_no

    db.commit()
    db.refresh(find_user)
    logger.info(f"User Login: {find_user.email}")
    return {"message": "User detail update successfully", "detail": find_user}


@user_router.patch("/reset_password")
def reset_password(
    token: str, user: ResetPasswordSchema, db: Session = Depends(get_db)
):
    user_detail = decode_token(token)
    id, name, email, phone_no = user_detail

    find_user = (
        db.query(UserModel)
        .filter(
            UserModel.email == email,
            UserModel.is_active == True,
            UserModel.is_verified == True,
            UserModel.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        raise HTTPException(status_code=404, detail="User not found")

    pass_checker(user.old_password, find_user.password)

    if user.new_password == user.confirm_password:
        setattr(find_user, "password", pwd_context.hash(user.confirm_password))
    else:
        raise HTTPException(
            status_code=400, detail="New password and confirm password does not match"
        )

    db.commit()
    db.refresh(find_user)

    logger.info(f"User Login: {find_user.email}")

    return "Password reset successfully"


@user_router.post("/generate_otp_for_forget_password")
def generate_otp_for_forget_password(email: str):
    Gen_OTP(email)
    logger.info(f"OTP Generate successfully : {email}")
    return "OTP generated successfully"


@user_router.patch("/forget_password")
def forget_password(
    email: str, otp: str, user: ForgetPasswordSchema, db: Session = Depends(get_db)
):
    logger.info(f"Forget password request received for email: {email}")

    find_user = (
        db.query(UserModel)
        .filter(
            UserModel.email == email,
            UserModel.is_active == True,
            UserModel.is_deleted == False,
            UserModel.is_verified == True,
        )
        .first()
    )

    if not find_user:
        logger.warning(f"User not found for email: {email}")
        raise HTTPException(status_code=404, detail="User not found")

    find_otp = (
        db.query(OTPModel).filter(OTPModel.email == email, OTPModel.otp == otp).first()
    )

    if not find_otp:
        logger.warning(f"Invalid OTP for email: {email}")
        raise HTTPException(status_code=404, detail="OTP not found")

    if user.new_password == user.confirm_password:
        setattr(find_user, "password", pwd_context.hash(user.confirm_password))
        logger.info(f"Password changed successfully for user ID: {find_user.id}")
    else:
        logger.error(
            f"Password mismatch for email: {email}. New and confirm passwords do not match."
        )
        raise HTTPException(
            status_code=400, detail="New password and confirm password does not match"
        )

    db.delete(find_otp)
    db.commit()
    db.refresh(find_user)
    logger.info(f"User Password change: {find_user.email}")
    return "Password change successfully"


@user_router.get("/get_all_user")
def get_all_user(db: Session = Depends(get_db)):
    find_user = (
        db.query(UserModel)
        .filter(
            UserModel.is_active == True,
            UserModel.is_verified == True,
            UserModel.is_deleted == False,
        )
        .all()
    )

    if not find_user:
        raise HTTPException(status_code=404, detail="No active user found")
    logger.info(f"User Get Successfully: {find_user}")
    return find_user


@user_router.delete("/delete_profile")
def delete(token: str, db: Session = Depends(get_db)):
    user_detail = decode_token(token)
    id, username, email, phone_no = user_detail
    find_user = (
        db.query(UserModel)
        .filter(
            UserModel.id == id,
            UserModel.is_active == True,
            UserModel.is_verified == True,
            UserModel.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        raise HTTPException(status_code=400, detail="User not found")

    find_user.is_deleted = True
    find_user.is_verified = False
    find_user.is_active = False

    db.commit()
    db.refresh(find_user)
    logger.info(f"User delete: {find_user.email}")
    return "User deleted successfully"


from src.models.post import PostModel


@user_router.get("/get_user_profile")
def user_profile(token: str, db: Session = Depends(get_db)):
    user_detail = decode_token(token)
    id, username, email, phone_no = user_detail

    find_user = (
        db.query(UserModel)
        .filter(
            UserModel.id == id,
            UserModel.is_active == True,
            UserModel.is_verified == True,
            UserModel.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        raise HTTPException(status_code=404, detail="User not found")

    find_post = (
        db.query(PostModel)
        .filter(PostModel.user_id == id, PostModel.is_deleted == False)
        .all()
    )

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    logger.info(f"User profile get successfully: {find_user.email}")

    return {
        "message": "User details",
        "user_id": find_user.id,
        "username": find_user.username,
        "email": find_user.email,
        "phone_no": find_user.phone_no,
        "is_verified": find_user.is_verified,
        "created_at": find_user.created_at,
        "Post details": find_post,
    }


from fastapi import Query
from sqlalchemy import select, func


# Pagination
@user_router.get("/get_user")
def get_task(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    total_users = db.execute(select(func.count()).select_from(UserModel)).scalar()
    Query = select(UserModel).limit(limit).offset(offset)
    result = db.execute(Query).scalars().all()
    return {
        "total_records": total_users,
        "limit": limit,
        "offset": offset,
        "users": result,
    }


# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from sqlalchemy import select, func
# from database.database import get_db
# from src.schemas.user import (
#     UserCreateSchema, UserUpdateSchema, ResetPasswordSchema, ForgetPasswordSchema,
# )
# from src.models.user import UserModel, OTPModel
# from src.utils.user import pwd_context, Gen_OTP, pass_checker, get_token, decode_token
# from logs.log_config import logger
# import uuid

# user_router = APIRouter(tags=["User"])

# @user_router.post("/signup")
# def create_new_user(user: UserCreateSchema, db: Session = Depends(get_db)):
#     try:
#         validate_email(user.email)
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid email format")

#     if db.query(UserModel).filter(UserModel.email == user.email).first():
#         raise HTTPException(status_code=400, detail="Email already exists")

#     new_user = UserModel(
#         username=user.username,
#         email=user.email,
#         phone_no=user.phone_no,
#         password=pwd_context.hash(user.password),
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     logger.info(f"New user signed up: {user.email[:3]}****")
#     return {
#         "message": "User Signup successful. Proceed to verification.",
#         "user_id": new_user.id,
#         "email": new_user.email,
#         "username": new_user.username,
#         "phone_no": new_user.phone_no,
#     }

# @user_router.post("/generate_OTP")
# def generate_otp(email: str):
#     Gen_OTP(email)
#     logger.info(f"OTP sent to: {email[:3]}****")
#     return "OTP generated successfully. Proceed to verification."

# @user_router.get("/verify_otp")
# def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
#     user = db.query(UserModel).filter(
#         UserModel.email == email,
#         UserModel.is_active == True,
#         UserModel.is_verified == False,
#         UserModel.is_deleted == False,
#     ).first()

#     if not user:
#         raise HTTPException(status_code=400, detail="User not found")

#     otp_entry = db.query(OTPModel).filter(OTPModel.email == email, OTPModel.otp == otp).first()
#     if not otp_entry:
#         raise HTTPException(status_code=400, detail="Invalid OTP")

#     user.is_verified = True
#     db.commit()
#     db.refresh(user)
#     logger.info(f"User verified: {email[:3]}****")
#     return "OTP verified successfully"

# @user_router.get("/login")
# def login(email: str, password: str, db: Session = Depends(get_db)):
#     user = db.query(UserModel).filter(
#         UserModel.email == email,
#         UserModel.is_active == True,
#         UserModel.is_deleted == False,
#         UserModel.is_verified == True,
#     ).first()

#     if not user:
#         raise HTTPException(status_code=400, detail="User not found")

#     pass_checker(password, user.password)
#     access_token = get_token(user.id, user.username, user.email, user.phone_no)
#     logger.info(f"User logged in: {email[:3]}****")
#     return {"message": "User login successful", "token": access_token}

# @user_router.patch("/update_user")
# def update_user(token: str, user: UserUpdateSchema, db: Session = Depends(get_db)):
#     user_detail = decode_token(token)
#     id, _, _, _ = user_detail
#     user_obj = db.query(UserModel).filter(UserModel.id == id).first()
#     if not user_obj:
#         raise HTTPException(status_code=404, detail="User not found")

#     user_obj.username = user.username
#     user_obj.email = user.email
#     user_obj.phone_no = user.phone_no
#     db.commit()
#     db.refresh(user_obj)
#     logger.info(f"User updated: {user_obj.email[:3]}****")
#     return {"message": "User details updated successfully"}

# @user_router.get("/get_all_users")
# def get_all_users(db: Session = Depends(get_db)):
#     users = db.query(UserModel).filter(
#         UserModel.is_active == True,
#         UserModel.is_verified == True,
#         UserModel.is_deleted == False,
#     ).all()
#     if not users:
#         raise HTTPException(status_code=404, detail="No active users found")
#     logger.info(f"Fetched {len(users)} active users")
#     return users

# @user_router.delete("/delete_profile")
# def delete_profile(token: str, db: Session = Depends(get_db)):
#     user_detail = decode_token(token)
#     id, _, _, _ = user_detail
#     user = db.query(UserModel).filter(UserModel.id == id).first()
#     if not user:
#         raise HTTPException(status_code=400, detail="User not found")

#     user.is_deleted = True
#     db.commit()
#     logger.info(f"User deleted: {user.email[:3]}****")
#     return "User deleted successfully"

# @user_router.get("/get_users")
# def get_users(db: Session = Depends(get_db), offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
#     total_users = db.query(func.count(UserModel.id)).scalar()
#     users = db.query(UserModel).offset(offset).limit(limit).all()
#     return {"total_records": total_users, "users": users}
