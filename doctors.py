#COMMIT TO MASTER ONLY

from sqlalchemy.orm import Session
from fastapi import status, Depends, APIRouter

from database.db import get_db

from model.doctors_model import Doctor
from schema.users_shema import user

import oauth

from schema.choices import available

app = APIRouter(tags = ["Doctors"])



@app.post("/doctors")
def doctors(choice: available, db:Session= Depends(get_db), current_user: user = Depends(oauth.get_current_user)):

    if choice == "Available":
        results = (
            db.query(
                Doctor.id,
                Doctor.name,
                Doctor.title,
                Doctor.is_available
            )
            .filter(Doctor.is_available == True)            
            .all()
        )

    else:
        results = (
            db.query(
                Doctor.id,
                Doctor.name,
                Doctor.title,
                Doctor.is_available
            ).all()
        )
    return [{'id': id, 'name': name, 'title': title, 'is_available': is_available} for (id, name, title, is_available) in results]




@app.post("/doctor_profile/{id}")
def doctor_profile(id: int, db:Session= Depends(get_db)):
    doctor = db.query(
            #Doctor.id,
            Doctor.name,
            Doctor.title,
            Doctor.mobile,
            Doctor.description,
            Doctor.is_available
    ).filter(Doctor.id == id).first()

    if doctor:
        return {'name': doctor.name, 
                'title': doctor.title, 
                'mobile': doctor.mobile,
                'about': doctor.description,
                'is_available': doctor.is_available}
    else:
        return {'message': status.HTTP_404_NOT_FOUND, "Detail": "Does not exist"}