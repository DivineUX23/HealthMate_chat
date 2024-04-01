from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, DateTime, Boolean
from database.db import Base
from datetime import datetime, timedelta

from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

    sessions = relationship('Session', back_populates='user')


class Session(Base):

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    conversation_id = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships

    user = relationship('User', back_populates='sessions')
    messages = relationship('Message', back_populates='sessions')
    ai_response = relationship('Ai_Response', back_populates='sessions')
    chat_history = relationship('ChatHistory', back_populates='session',  uselist=False)



class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), unique=True)
    chat_history = Column(JSON, default=None, nullable=False)

    session = relationship('Session', back_populates='chat_history')



class Message(Base):

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    text = Column(Text, nullable=False)
    is_user_message = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    sessions = relationship('Session', back_populates='messages')
    ai_response = relationship('Ai_Response', back_populates='message', uselist=False)  # One-to-one relationship



class Ai_Response(Base):

    __tablename__ = 'ai_response'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    sessions = relationship('Session', back_populates='ai_response')
    message = relationship('Message', back_populates='ai_response')
