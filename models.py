import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_password = db.Column(db.String, nullable=False)

class ChatRoom(db.Model):
    __tablename__ = "chatroom"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    creator = db.Column(db.String, nullable=False)
