# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


# Создаём db, но НЕ привязываем к app сразу
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


@login_manager.user_loader
def load_user(user_id):
    from .models import User  # импорт внутри функции, чтобы избежать циклического импорта
    return User.query.get(int(user_id))