#COMMIT TO MASTER ONLY

from pydantic import BaseModel, root_validator, EmailStr
from model.users_model import User
from model.doctors_model import Doctor

from database.db import SessionLocal
from fastapi import HTTPException, status


class doctor(BaseModel):

    name: str
    email: EmailStr
    password: str
    mobile: str
    description: str
    title: str

    class Config:
        from_attributes = True

class show_doctor(BaseModel):
    name: str
    email: str
    mobile: int
    #description: str    
    title: str


    class Config:
        from_attributes = True

class login(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None


class CreateUser(doctor):
    password: str

    class Config:

        from_attributes = True

    @root_validator(pre=True)
    @classmethod
    def validate_email(cls, values):
        email = values.get("email")

        with SessionLocal() as db:
            user_email = db.query(Doctor).filter(Doctor.email == email).first()
            if user_email:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f"Email already exists.")
        
        return values