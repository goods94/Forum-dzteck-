from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
import time

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120))
    avatar = db.Column(db.String(255))
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.Float, default=time.time)
    threads = db.relationship('Thread', backref='author_user', lazy=True)
    reactions = db.relationship('Reaction', backref='user', lazy=True)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.Float, default=time.time)
    reactions = db.relationship('Reaction', backref='thread', lazy=True)

class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    emoji = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.Float, default=time.time)