# backend/routes/auth.py

from flask import Blueprint, request, jsonify, session, current_app, redirect, url_for
from ..models import User, UserOrfoData
from ..extensions import db, mail, limiter
from flask_mail import Message
from datetime import datetime, timedelta
import re
import json
import traceback
from flask_limiter.util import get_remote_address
from flask_login import current_user



auth_bp = Blueprint('auth', __name__)



def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# # ✉️ Функция отправки письма — встроена прямо здесь (как в project_webmath)
# def send_registration_email(email, username, token, app):
#     try:
#         verify_link = f"http://localhost:5006/api/verify-email?token={token}"
        
#         msg = Message(
#             subject='Подтверждение регистрации — NeuroStat',
#             sender=app.config.get('MAIL_DEFAULT_SENDER', 'neurostat@bk.ru'),
#             recipients=[email]
#         )
#         msg.body = f'''Привет, {username}!

# Спасибо за регистрацию в NeuroStat.

# Пожалуйста, подтвердите ваш email, перейдя по ссылке:
# {verify_link}

# Если вы не регистрировались — просто проигнорируйте это письмо.

# С уважением,
# Команда NeuroStat
# '''
#         msg.html = f'''
#         <h3>Привет, {username}!</h3>
#         <p>Спасибо за регистрацию в <b>NeuroStat</b>.</p>
#         <p>Пожалуйста, <a href="{verify_link}">подтвердите ваш email</a>.</p>
#         <p><small>Если вы не регистрировались — просто проигнорируйте это письмо.</small></p>
#         <hr>
#         <small>С уважением,<br>Команда NeuroStat</small>
#         '''
#         mail.send(msg)
#     except Exception as e:
#         raise e  # пробрасываем ошибку, чтобы она попала в лог в register()

# Временно упростим отправку email для отладки
def send_registration_email(email, username, token, app):
    try:
        verify_link = f"http://localhost:5006/api/verify-email?token={token}"
        print(f"=== EMAIL FOR {email} ===")
        print(f"Verify link: {verify_link}")
        print("========================")
        
        # Пока отключим реальную отправку для тестов
        # msg = Message(
        #     subject='Подтверждение регистрации — NeuroStat',
        #     sender=app.config.get('MAIL_DEFAULT_SENDER', 'neurostat@bk.ru'),
        #     recipients=[email]
        # )
        # msg.body = f'''Привет, {username}!...'''
        # mail.send(msg)
        
    except Exception as e:
        print(f"Email error: {e}")


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("3 per 1 minutes")
def register():
    print("[DEBUG] /register endpoint called")  # Добавим логирование
    data = request.get_json()
    print("[DEBUG] Received data:", data)
    
    if not data:
        print("[DEBUG] No JSON data received")
        return jsonify({"error": "No data received"}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Валидация входных данных
    if not username or not email or not password:
        return jsonify({"error": "Username, email and password required"}), 400

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # Создание пользователя
    user = User(username=username, email=email)
    user.set_password(password)
    user.generate_verify_token()

    print("[DEBUG] User object created:", user)
    print("[DEBUG] User.password_hash:", user.password_hash)
    print("[DEBUG] User.verify_token:", user.verify_token)

    try:
        db.session.add(user)
        print("[DEBUG] User added to session")
        db.session.commit()
        print(f"[SUCCESS] User {username} saved to database with ID: {user.id}")
    except Exception as db_error:
        db.session.rollback()
        print(f"[CRITICAL DB ERROR] Failed to save user: {str(db_error)}")
        print(traceback.format_exc())
        return jsonify({"error": "Registration failed due to server error"}), 500

    # Отправка письма
    try:
        send_registration_email(user.email, user.username, user.verify_token, current_app._get_current_object())
        print(f"[SUCCESS] Verification email sent to {user.email}")
    except Exception as mail_error:
        print(f"[MAIL ERROR] Failed to send email to {user.email}: {str(mail_error)}")
        print(traceback.format_exc())

    print(f"[DEV] Verify link: http://localhost:5006/api/verify-email?token={user.verify_token}")

    return jsonify({
        "message": "User registered successfully. Please check your email to verify your account.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 201


@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token required"}), 400

    user = User.query.filter_by(verify_token=token).first()
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 400

    if user.verify_token and (datetime.utcnow() - user.created_at) > timedelta(hours=24):
        return jsonify({"error": "Token expired"}), 400  # исправил опечатку "expireded"

    user.email_verified = True
    user.verify_token = None
    db.session.commit()

    # 👇 Автоматически входим в систему после подтверждения email
    session['user_id'] = user.id

    return redirect('/frontend/index.html')



@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    session['user_id'] = user.id

    return jsonify({
        "message": "Logged in successfully",
        "user_id": user.id,
        "username": user.username
    }), 200



@auth_bp.route('/user/data', methods=['GET', 'POST'])
def user_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(user_id)

    if request.method == 'POST':
        data = request.get_json()
        user.user_data = json.dumps(data)
        db.session.commit()
        return jsonify({"message": "Data saved", "data": data}), 200

    elif request.method == 'GET':
        return jsonify({"data": json.loads(user.user_data) if user.user_data else {}}), 200
    
    
    
@auth_bp.route('/user/profile', methods=['GET'])
def user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email,
        "email_verified": user.email_verified
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)  # Удаляем user_id из сессии
    return jsonify({"message": "Logged out successfully"}), 200


# --- Сохранение данных орфографии ---
@auth_bp.route('/save-orfo', methods=['POST'])
def save_orfo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    print("[DEBUG] Save-orfo received:", data)
    
    field_name = data.get('field')
    content = data.get('content')

    if not field_name:
        return jsonify({"error": "field is required"}), 400

    # Находим или создаём запись
    record = UserOrfoData.query.filter_by(user_id=user_id, field_name=field_name).first()
    if record:
        record.content = content
    else:
        record = UserOrfoData(user_id=user_id, field_name=field_name, content=content)
        db.session.add(record)

    db.session.commit()
    print("[DEBUG] Record committed to DB")
    
    return jsonify({"status": "saved"}), 200


# --- Загрузка данных орфографии ---
@auth_bp.route('/load-orfo', methods=['GET'])
def load_orfo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    records = UserOrfoData.query.filter_by(user_id=user_id).all()
    data = {record.field_name: record.content for record in records}
    return jsonify(data), 200