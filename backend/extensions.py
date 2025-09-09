# backend/extensions.py

from flask_sqlalchemy import SQLAlchemy

# Создаём db, но НЕ привязываем к app сразу
db = SQLAlchemy()