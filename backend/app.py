# backend/app.py

from flask import Flask, session
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import db, login_manager, mail
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-for-dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app, origins=["http://localhost:8000"])

    # 👇 Инициализируем db с приложением
    db.init_app(app)

    # 👇 Импортируем модели (чтобы они зарегистрировались в db)
    from models import User
    
    mail.init_app(app)

    # 👇 Регистрируем маршруты
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    # Создаём таблицы
    with app.app_context():
        db.create_all()

    @app.route('/')
    def hello():
        return {"message": "NeuroStat API is running"}

    return app





if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5006
        )