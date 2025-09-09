# backend/routes/auth.py

from flask import Blueprint, request, jsonify, session
from models import User
from extensions import db, mail  # ← импортируем db из extensions
from flask_mail import Message
import re
import json
import uuid
import traceback

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern) is not None


def send_registration_email(email, username):
    try:
        msg = Message(
            subject='Подтверждение регистрации — NeuroStat',
            sender=('NeuroStat', 'neurostat@bk.ru'),
            recipients=[email]
        )
        msg.body = f'''Привет, {username}!

Спасибо за регистрацию в NeuroStat.

Это тестовое письмо — подтверждение регистрации.

С уважением,
Команда NeuroStat
'''
        msg.html = f'''
        <h3>Привет, {username}!</h3>
        <p>Спасибо за регистрацию в <b>NeuroStat</b>.</p>
        <p>Это тестовое письмо — подтверждение регистрации.</p>
        <hr>
        <small>С уважением,<br>Команда NeuroStat</small>
        '''
        mail.send(msg)
        print(f"[SUCCESS] Письмо отправлено на {email}")
    except Exception as e:
        print(f"[ERROR] Не удалось отправить письмо на {email}: {str(e)}")
        print(traceback.format_exc())  # вывод полной ошибки



@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')  # ← новый параметр
    email = data.get('email')
    password = data.get('password')

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

    user = User(username=username, email=email)  # ← передаём username
    user.set_password(password)
    user.generate_verify_token()
    db.session.add(user)
    db.session.commit()
    
    try:
        send_registration_email(user.email, user.username)
    except Exception as e:
        print(f"[ERROR] Не удалось отправить письмо: {e}")
        # Можно добавить flash-сообщение пользователю, но для MVP — просто логируем

    print(f"[DEV] Verify link: http://localhost:5000/api/verify-email?token={user.verify_token}")

    return jsonify({"message": "User registered. Check email to verify."}), 201



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