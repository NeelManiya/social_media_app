from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    phone_no: str
    password: str


class UserUpdateSchema(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    phone_no: Optional[str]


class ResetPasswordSchema(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


class ForgetPasswordSchema(BaseModel):
    new_password: str
    confirm_password: str
