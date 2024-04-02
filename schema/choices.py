#COMMIT TO MASTER ONLY

from pydantic import BaseModel, root_validator
from model.users_model import User
from database.db import SessionLocal
from fastapi import HTTPException, status
from enum import Enum


class available(str, Enum):
    NO = "Unavailable"
    YES = "Available"
    

class current_user(str, Enum):
    USER = "Patient"
    DOCTOR = "Medical practionier"