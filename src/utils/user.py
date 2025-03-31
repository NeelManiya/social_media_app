from database.database import get_db, SessionLocal
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.user import UserModel
from src.models.user import OTPModel

db = SessionLocal()

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def pass_checker(user_pass, hash_pass):
    if pwd_context.verify(user_pass, hash_pass):
        return True
    else:
        raise HTTPException(status_code=400, detail="Password is incorrect")


import random
import uuid


def Gen_OTP(email: str):
    find_user = (
        db.query(UserModel)
        .filter(
            UserModel.email == email,
            UserModel.is_active == True,
            # UserModel.is_verified == False,
            UserModel.is_deleted == False,
        )
        .first()
    )

    if not find_user:
        raise HTTPException(status_code=400, detail="User not found")

    random_otp = random.randint(1000, 9999)

    print(random_otp)

    new_otp = OTPModel(
        email=find_user.email,
        user_id=find_user.id,
        otp=random_otp,
    )

    send_email(find_user.email, "Login Email", f"OTP is {random_otp}")

    db.add(new_otp)
    db.commit()
    db.refresh(new_otp)
    return "OTP verified successfully"


from datetime import datetime, timezone, timedelta
import jwt
from config import ALGORITHM, SECRET_KEY


def get_token(id: str, username: str, email: str, phone_no: int):
    try:
        payload = {
            "id": id,
            "username": username,
            "email": email,
            "phone_no": phone_no,
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        }
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id = payload.get("id")
        username = payload.get("username")
        email = payload.get("email")
        phone_no = payload.get("phone_no")

        if not id or not username or not email or not phone_no:
            raise HTTPException(status_code=403, detail="Invalid token")
        return id, username, email, phone_no

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=403, detail="Invalid token")


from config import SENDER_EMAIL, EMAIL_PASSWORD
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def send_email(receiver, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = SENDER_EMAIL
    smtp_pass = EMAIL_PASSWORD

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(SENDER_EMAIL, receiver, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail="Email sending failed")
