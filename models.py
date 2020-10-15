import os

from flask import Flask
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    user_name = Column(String, nullable=False)
    user_password = Column(String, nullable=False)

class ChatRoom(Base):
    __tablename__ = "chatroom"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    creator = Column(String, nullable=False)
