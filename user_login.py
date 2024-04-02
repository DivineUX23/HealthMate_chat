from fastapi import APIRouter, Depends,  status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import token_key
from database.db import get_db
from model.users_model import User
from model.doctors_model import Doctor
from schema import users_shema
from schema.choices import current_user

from sqlalchemy.orm import Session
from hashing import hash

app = APIRouter(tags=['User'])


#TESTING ONLY:


@app.post("/login/patient")
async def login_patient(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token, data = authenticate_user(db, request.username, request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {'role': data, 'access_token': token, 'token_type': 'bearer'}

@app.post("/login/doctor")
async def login_doctor(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token, data = authenticate_doctor(db, request.username, request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {'role': data, 'access_token': token, 'token_type': 'bearer'}



#COMMIT TO MASTER ONLY

@app.post("/login")
async def login(user_type: current_user, request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    if user_type not in ["Patient", "Medical practitioner"]:
        raise HTTPException(status_code=400, detail="Invalid user type")

    if user_type == "Patient":
        token, data = authenticate_user(db, request.username, request.password)
    elif user_type == "Medical practionier":
        token, data = authenticate_doctor(db, request.username, request.password)

    if not token:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    return {'role': data, 'access_token': token, 'token_type': 'bearer'}



def authenticate_user(db: Session, username: str, password: str):
    user=db.query(User).filter(User.email == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{user} does not exist")

    if not hash.verify(user.password, password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"password incorrect")

    data={"sub": user.email, "id": user.id, "role": "client"}

    token = token_key.create_access_token(data)

    return token, data["role"]





def authenticate_doctor(db: Session, username: str, password: str):
    
    user = db.query(Doctor).filter(Doctor.email == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{user} does not exist")

    if not hash.verify(user.password, password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"password incorrect")

    data={"sub": user.email, "id": user.id, "role": "client"}

    token = token_key.create_access_token(data)

    return token, data["role"]



"""
@app.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends(), db: Session= Depends(get_db)):
    user=db.query(User).filter(User.email == request.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hate to say but {user} does not exist")

    if not hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hate to say but your password is incorrect")


    token = token_key.create_access_token(data={"sub": user.email})
    
    return {'access_token': token, 'token_type': 'bearer'}

"""