from typing import Optional, List, Tuple
import logging
from sqlalchemy.exc import SQLAlchemyError

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
import json

from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi import FastAPI,HTTPException,status, Depends
from database.db import get_db

from schema.users_shema import user
import oauth
from sqlalchemy import func

import jsonpickle
import os
from dotenv import load_dotenv
import uuid

from model.users_model import User, ChatHistory
from model import users_model

from .prompt import gemini_search_prompt

from datetime import datetime

logger = logging.getLogger(__name__)

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")
google_api_key = os.getenv("GOOGLE_API_KEY")


class Gemini:
    def __init__(self, old_session: Optional[Session] = None, db: Session = Depends(get_db), current_user: user = Depends(oauth.get_current_user)):
        self.description = gemini_search_prompt
        self.db = db
        self.current_user = current_user
        self.agent_executor = None

        if old_session != None:
            self.session = old_session
            print(old_session.conversation_id)

        else:
            self.create_new_session()
            print(f"new session {self.session.conversation_id}")


    def create_new_session(self):
        new_session = users_model.Session(
            user_id=self.current_user.id,
            conversation_id=f"user_{self.current_user.id}_{str(uuid.uuid4())}"
        )
        self.db.add(new_session)
        self.db.commit()
        self.session = new_session


    def _get_current_user(self):
        try:
            chat_history = self.db.query(User).filter(self.current_user.id == User.id).first()
            print(chat_history)
            return chat_history

        except Exception as e:
            #logger.error(f"Error fetching user from DB: {e}")
            print(f"Error fetching user from DB: {e}")
            return f"Error fetching user from DB: {e}"


    def google_search(self):

        try:
            search = GoogleSearchAPIWrapper(google_api_key=google_api_key, google_cse_id=google_cse_id)

            google_tool = Tool(
                name = "google_search",
                description = self.description,
                func = search.run,
            )
            return [google_tool]
            
        except Exception as e:
            print(f"Error fetching google_search tool: {e}")
            #logger.error(f"Error fetching user from DB: {e}")


    def gemini(self, message):

        try:
            google_tool = self.google_search()
            input = f"""Diagnose and suggest remedies for this user's codition. Through active listening and follow-up questions, gather detailed information about the user's symptoms to determine the specific condition. Ask probing questions, just like a doctor would, to pinpoint the exact ailment before providing potential diagnoses. keep your response consice and well structured.
                                            User: {message} 
                                            Medical chatbot: """
                
            llm = ChatGoogleGenerativeAI(temperature=0.1, model="gemini-pro", google_api_key=gemini_api_key)
            prompt = ChatPromptTemplate.from_messages(
                [
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("user", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

            llm_with_tools = llm.bind(functions=google_tool)
            agent = self.creat_agent(prompt, llm_with_tools)
            run = self.run_agent(agent, google_tool, message, input)
            return run
        
        except Exception as e:
            print(f"Error exceuting code: {e}")
            return "Error executing your request, try again"



    def creat_agent(self, prompt, llm_with_tools):

        try:
            agent = (
                {
                    "input":lambda x: x["input"],
                    "chat_history":lambda x: x["chat_history"],
                    "agent_scratchpad": lambda x: format_to_openai_function_messages(
                        x["intermediate_steps"]
                    ),
                }
                | prompt
                | llm_with_tools
                | OpenAIFunctionsAgentOutputParser()
            )
            return agent
        
        except Exception as e:
            print(f"Error seetin_up agent: {e}")



    def run_agent(self, agent, google_tool, message, input):
        
        try:
            if self.session.chat_history:
                print(self.session.chat_history)
                chat_history = jsonpickle.decode(self.session.chat_history.chat_history)
            else:
                chat_history = []

            print(chat_history)

            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=google_tool, 
                verbose=True, 
                return_intermediate_steps=True, 
                handle_parsing_errors=True,
            )

            result = self.agent_executor.invoke({"input": input, "chat_history": chat_history})
            chat_history.extend(
                [
                    HumanMessage(content=input),
                    AIMessage(content=result["output"]),
                ]
            )

            self.save_conversation(message = message,
                                result = result["output"], 
                                chat_history = chat_history)

            print(f"this------------\n\n\n{result['output']}\n\n\n")

            return result['output']
    
        except Exception as e:
            print(f"Error running agent: {e}")



    def save_conversation(self, message, result, chat_history):
        try:
            history_json = jsonpickle.encode(chat_history)

            existing_chat_history = self.db.query(users_model.ChatHistory).filter_by(session_id=self.session.id).first()

            if existing_chat_history:
                existing_chat_history.chat_history = history_json
            else:
                conversation_history = users_model.ChatHistory(
                    session_id = self.session.id,
                    chat_history = history_json,
                )
                self.db.add(conversation_history)


            user_message = users_model.Message(
                session_id = self.session.id,                
                text = message,
            )
            self.db.add(user_message)
            self.db.flush()  
            
            print(f"CHAT_ID{user_message.id}")
            

            ai_response = users_model.Ai_Response(
                session_id = self.session.id,
                message_id = user_message.id,
                text = result,
            )
            self.db.add(ai_response)

            self.db.commit()    
        except SQLAlchemyError as e:
            logger.error(f"Error saving conversation to DB: {e}")
            self.db.rollback()  
         


def start_session(session_id: Optional[str] = None, db: Session = Depends(get_db), current_user: user = Depends(oauth.get_current_user)):
    
    if session_id != None:
        old_session = db.query(users_model.Session).filter(users_model.Session.conversation_id == session_id).first()
            
        if old_session.user_id != current_user.id:
            return None, {"error": "Session not found"}
        else:

            chat = []

            gemini = Gemini(old_session, db, current_user)
        
            if old_session:
                for message in old_session.messages:
                    chat_entry = {"User": message.text}
                    if message.ai_response:
                        chat_entry["Medichat"] = message.ai_response.text
                    else:
                        chat_entry["Medichat"] = "AI response not available"
                    
                    chat.append(chat_entry)
            
                print(message.ai_response)

                print(chat)
            else:
                return None, [{"error": "Session not found"}]
        
            return gemini, chat
    
    else:
        gemini = Gemini(session_id, db, current_user)
        print(session_id) 

        return gemini, "New chat"


def all_session(db:Session= Depends(get_db), current_user: user = Depends(oauth.get_current_user)):


    subquery = (
        db.query(
            users_model.Message.session_id.label('session_id'),
            func.min(users_model.Message.id).label('min_id')
        )
        .group_by(users_model.Message.session_id)
        .subquery()
    )

    results = (
        db.query(
            users_model.Session.created_at,
            users_model.Session.conversation_id,
            users_model.Message.text.label('first_message')
        )
        .join(subquery, users_model.Session.id == subquery.c.session_id)
        .join(users_model.Message, users_model.Message.id == subquery.c.min_id)
        .filter(users_model.Session.user_id == current_user.id)
        .all()
    )


    return results


def run(input: str, gemini_session: tuple = Depends(start_session)):
    

    gemini, message = gemini_session
    result = gemini.gemini(input)
    
    print({"AI":result})

    return {"AI":result}
