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
    return {
        "message": "User Signup successfully, Now go for verification",
        "user_id": new_user.id,
        "username": new_user.username,
        "phone_no": new_user.phone_no,
        "email": new_user.email,
    }


@user_router.post("/generate_OTP")
def Generate_OTP(email: str):
    Gen_OTP(email)
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

    return {
        "message": "User login successfully",
        "id": find_user.id,
        "username": find_user.username,
        "email": find_user.email,
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

    return "Password reset successfully"


@user_router.post("/generate_otp_for_forget_password")
def generate_otp_for_forget_password(email: str):
    Gen_OTP(email)
    return "OTP generated successfully"


@user_router.patch("/forget_password")
def forget_password(
    email: str, otp: str, user: ForgetPasswordSchema, db: Session = Depends(get_db)
):
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
        raise HTTPException(status_code=404, detail="User not found")

    find_otp = (
        db.query(OTPModel).filter(OTPModel.email == email, OTPModel.otp == otp).first()
    )

    if not find_otp:
        raise HTTPException(status_code=404, detail="OTP not found")

    if user.new_password == user.confirm_password:
        setattr(find_user, "password", pwd_context.hash(user.confirm_password))
    else:
        raise HTTPException(
            status_code=400, detail="New password and confirm password does not match"
        )

    db.delete(find_otp)
    db.commit()
    db.refresh(find_user)
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
        .all()
    )

    if not find_user:
        raise HTTPException(status_code=404, detail="User not found")

    find_post = (
        db.query(PostModel)
        .filter(PostModel.id == id, PostModel.is_deleted == False)
        .first()
    )

    if not find_post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"Details for user": find_user, "Details for post": find_post}
