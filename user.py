from sqlalchemy.orm import Session
from fastapi import status, HTTPException, Depends, APIRouter
from hashing import hash
from database.db import get_db
from model.users_model import User
from schema.users_shema import user
from schema.users_shema import show_user
from hashing import hash
import services.user_services
from uuid import uuid4



from schema.users_shema import user
from schema.doctors_schema import doctor, show_doctor

import oauth

from model.users_model import User
from hashing import hash

from model.doctors_model import Doctor
from schema.choices import available

app = APIRouter(tags= ["User"])


@app.post("/sign_up")
async def sign_up(user: user, db: Session = Depends(get_db)):

    new_users = services.user_services.sign_up(user=user, db=db)

    verification_token = str(uuid4())
    
    new_users.verification_token = verification_token
    db.commit()

    return {'message': "User created successfully.", 'detail': show_user.from_orm(new_users)}



#COMMIT TO MASTER ONLY

@app.post("/doctor_sign_up")
async def sign_up(doctor: doctor, db: Session = Depends(get_db)):

    new_doctor = services.user_services.doctor_sign_up(doctor=doctor, db=db)
  
    verification_token = str(uuid4())
    
    new_doctor.verification_token = verification_token
    db.commit()

    return {'message': "User created successfully.", 'detail': show_doctor.from_orm(new_doctor)}




@app.post("/doctor_available")
async def available(choice: available, db: Session = Depends(get_db), current_user: doctor = Depends(oauth.get_current_doctor)):

    if choice == "Available":
        current_user.is_available = True
    else:
        current_user.is_available = False

    db.commit()              

    return {'message': f"You are now {choice} for calls."}
