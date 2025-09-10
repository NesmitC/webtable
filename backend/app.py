from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from .extensions import db, login_manager, mail
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Секретный ключ
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-for-dev')
    
    # Настройки почты
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 465))
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'neurostat@bk.ru')
    
    # База данных
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///backend/instance/database.db')
    # Получаем абсолютный путь к backend/instance/database.db
    basedir = os.path.abspath(os.path.dirname(__file__))  # путь к backend/
    database_path = os.path.join(basedir, 'instance', 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CORS
    CORS(app, origins=["http://localhost:5500", "http://127.0.0.1:5500"])
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # маршрут для входа
    mail.init_app(app)

    # Импорт моделей (после инициализации!)
    from .models import User

    # Регистрация маршрутов
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    # Создание таблиц
    with app.app_context():
        db.create_all()

    # Главная страница
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