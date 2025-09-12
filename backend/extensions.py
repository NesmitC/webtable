# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Создаём db, но НЕ привязываем к app сразу
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "250 per hour"],
    storage_uri="memory://",  # для разработки
    strategy="fixed-window"
)


@login_manager.user_loader
def load_user(user_id):
    from .models import User  # импорт внутри функции, чтобы избежать циклического импорта
    return User.query.get(int(user_id))
