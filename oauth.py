from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import token_key
from typing import Annotated
from model.users_model import User
from model.doctors_model import Doctor
from database.db import get_db



#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

patient_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/patient")

def get_current_user(token: Annotated[str, Depends(patient_oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = token_key.verify_token(token, credentials_exception)

    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise credentials_exception
    return user

#COMMIT TO MASTER ONLY

doctor_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/doctor")

def get_current_doctor(token: Annotated[str, Depends(doctor_oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = token_key.verify_token(token, credentials_exception)

    doctor = db.query(Doctor).filter(Doctor.email == token_data.email).first()
    if not doctor:
        raise credentials_exception
    return doctor