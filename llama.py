from sqlalchemy.orm import Session
from fastapi import FastAPI, WebSocket, status, Depends, APIRouter, HTTPException
from typing import Optional

from database.db import get_db

from services.gemini import run, start_session, all_session

from schema.users_shema import user
import oauth
import json

fastapp = FastAPI()
app = APIRouter(tags = ["Llama"])
fastapp.include_router(app)

from services.gemini import start_session




@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, session_id: Optional[str] = None, db: Session = Depends(get_db)):
    
    await websocket.accept()
    
    current_user = websocket.query_params.get("token")

    user = oauth.get_current_user(current_user, db)

    if session_id:
        gemini, chat = start_session(session_id, db, user)
    else:
        gemini, chat = start_session(None, db, user)

    await websocket.send_text(json.dumps(chat))

    while True:
        data = await websocket.receive_text()
        print(data)
        result = gemini.gemini(data)
        
        await websocket.send_text(json.dumps(result))



@app.get("/all_chat/")

async def all_chats(db: Session = Depends(get_db), current_user: user = Depends(oauth.get_current_user)):

    result = all_session(db=db, current_user=current_user)

    return [{'title': text, 'date': created_at, 'id': id} for (created_at, id, text) in result]





#Conversation Endpoint, Testing purposes:
@app.post("/response/")

async def conversationing(input: str, gemini_session: tuple = Depends(start_session), db: Session = Depends(get_db), current_user: user = Depends(oauth.get_current_user)):

    result = run(input=input, gemini_session=gemini_session)

    return {'message': status.HTTP_200_OK, "Detail": result}

    
@app.post("/new_chat/")

async def start_chat(session_id: Optional[int] = None, db: Session = Depends(get_db), current_user: user = Depends(oauth.get_current_user)):

    gemini, result = start_session(session_id=session_id, db=db, current_user=current_user)

    return {'message': status.HTTP_200_OK, "Detail": result}
