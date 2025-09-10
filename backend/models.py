# backend/models.py

from .extensions import db  # ← импортируем db из extensions, а не из app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
import uuid
import secrets

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verify_token = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_data = db.Column(db.Text, default='{}')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verify_token(self):
        self.verify_token = str(uuid.uuid4())
        
    verify_token = db.Column(db.String(100), unique=True, nullable=True)
    def generate_verify_token(self):
        self.verify_token = secrets.token_urlsafe(50)