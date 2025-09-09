# backend/routes/auth.py

from flask import Blueprint, request, jsonify, session
from ..models import User
from ..extensions import db, mail  # ← импортируем db из extensions
from flask_mail import Message
import re
import json
import uuid
import traceback

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern) is not None



@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Валидация входных данных
    if not username or not email or not password:
        return jsonify({"error": "Username, email and password required"}), 400

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # Создание пользователя
    user = User(username=username, email=email)
    user.set_password(password)
    user.generate_verify_token()  # если используешь подтверждение по email

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as db_error:
        db.session.rollback()
        print(f"[DB ERROR] Failed to save user: {str(db_error)}")
        print(traceback.format_exc())
        return jsonify({"error": "Registration failed due to server error"}), 500

    # Отправка письма
    try:
        send_registration_email(user.email, user.username, user.verify_token)
        print(f"[SUCCESS] Verification email sent to {user.email}")
    except Exception as mail_error:
        # Не возвращаем ошибку клиенту — регистрация прошла, письмо можно отправить позже
        print(f"[MAIL ERROR] Failed to send email to {user.email}: {str(mail_error)}")
        print(traceback.format_exc())

    # Для разработки — выводим ссылку в консоль
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

    user.email_verified = True
    user.verify_token = None
    db.session.commit()

    return jsonify({"message": "Email verified successfully!"})



@auth_bp.route('/login', methods=['POST'])
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

    # 👇 Возвращаем username в ответе
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
        return jsonify({"data": json.loads(user.user_data)}), 200