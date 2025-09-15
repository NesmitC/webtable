// frontend\js\main.js

const API_URL = 'http://localhost:5006/api';

document.getElementById('btn-register').addEventListener('click', () => {
    document.getElementById('register-form').style.display = 'block';
    document.getElementById('login-form').style.display = 'none';
});

document.getElementById('btn-login').addEventListener('click', () => {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
});

document.getElementById('submit-register').addEventListener('click', async () => {
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const messageEl = document.getElementById('reg-message');

    if (!username || !email || !password) {
        messageEl.style.color = 'red';
        messageEl.textContent = 'Заполните все поля';
        return;
    }

    if (username.length < 3) {
        messageEl.style.color = 'red';
        messageEl.textContent = 'Логин должен быть не короче 3 символов';
        return;
    }

    if (password.length < 6) {
        messageEl.style.color = 'red';
        messageEl.textContent = 'Пароль должен быть не короче 6 символов';
        return;
    }

    const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });

    const result = await response.json();

    messageEl.style.color = response.ok ? 'green' : 'red';
    messageEl.textContent = result.message || result.error;

    if (response.ok) {
        alert('Проверьте почту — отправлено письмо с подтверждением!');
    }
});

document.getElementById('submit-login').addEventListener('click', async () => {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const messageEl = document.getElementById('login-message');

    const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include'
    });

    const result = await response.json();

    messageEl.style.color = response.ok ? 'green' : 'red';
    messageEl.textContent = result.message || result.error;

    if (response.ok) {
        showLoggedInState(result.username);
        document.getElementById('login-form').style.display = 'none';
    }
});

document.getElementById('btn-logout').addEventListener('click', async () => {
    const response = await fetch(`${API_URL}/logout`, {
        method: 'POST',
        credentials: 'include'
    });

    if (response.ok) {
        location.reload();
    } else {
        alert('Ошибка выхода');
    }
});

async function checkLoginStatus() {
    const response = await fetch(`${API_URL}/user/profile`, {
        method: 'GET',
        credentials: 'include'
    });

    if (response.ok) {
        const result = await response.json();
        document.getElementById('welcome-username').textContent = result.username;
        document.getElementById('welcome-message').style.display = 'block';
        showLoggedInState(result.username);
    }
}

function showLoggedInState(username) {
    document.getElementById('btn-logout').style.display = 'inline-block';
    document.getElementById('auth-buttons').querySelectorAll('button').forEach(btn => {
        if (btn.id !== 'btn-logout') btn.style.display = 'none';
    });

    // Показываем username в хедере
    document.getElementById('welcome-username').textContent = username;

    // Добавляем приветствие, если его ещё нет
    if (!document.querySelector('#welcome-message + p')) {
        const welcomeMsg = document.createElement('p');
        welcomeMsg.textContent = `Привет, ${username}!`;
        welcomeMsg.style.cssText = 'font-size: 1.2em; font-weight: bold; color: #2c3e50; margin: 10px 0;';
        document.querySelector('main h1').after(welcomeMsg);
    }
}

document.addEventListener('DOMContentLoaded', checkLoginStatus);