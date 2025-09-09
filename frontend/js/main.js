const API_URL = 'http://localhost:5000/api';

// Показать/скрыть формы
document.getElementById('btn-register').addEventListener('click', () => {
    document.getElementById('register-form').style.display = 'block';
    document.getElementById('login-form').style.display = 'none';
});

document.getElementById('btn-login').addEventListener('click', () => {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
});

// Регистрация
document.getElementById('submit-register').addEventListener('click', async () => {
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const messageEl = document.getElementById('reg-message');

    if (username.length < 3) {
        messageEl.style.color = 'red';
        messageEl.textContent = 'Логин должен быть не короче 3 символов';
        return;
    }

    const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    const result = await response.json();

    messageEl.style.color = response.ok ? 'green' : 'red';
    messageEl.textContent = result.message || result.error;

    if (response.ok) {
        alert('Проверьте консоль сервера — там ссылка для подтверждения email!');
    }
});

// Вход
document.getElementById('submit-login').addEventListener('click', async () => {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const messageEl = document.getElementById('login-message');

    const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include' // важно для сессий!
    });

    const result = await response.json();

    messageEl.style.color = response.ok ? 'green' : 'red';
    messageEl.textContent = result.message || result.error;

    if (response.ok) {
        // Показываем блок данных и кнопку выхода
        document.getElementById('user-data').style.display = 'block';
        document.getElementById('btn-logout').style.display = 'inline-block';
        document.getElementById('auth-buttons').querySelectorAll('button').forEach(btn => {
            if (btn.id !== 'btn-logout') btn.style.display = 'none';
        });

        // 👇 Отображаем приветствие с логином
        const welcomeMsg = document.createElement('p');
        welcomeMsg.textContent = `Привет, ${result.username}!`;
        welcomeMsg.style.fontSize = '1.2em';
        welcomeMsg.style.fontWeight = 'bold';
        welcomeMsg.style.color = '#2c3e50';
        document.querySelector('main h1').after(welcomeMsg);

    }
});

// Сохранение данных
document.getElementById('save-data').addEventListener('click', async () => {
    const data = document.getElementById('user-data-input').value;
    const messageEl = document.getElementById('data-message');

    const response = await fetch(`${API_URL}/user/data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: data }),
        credentials: 'include'
    });

    const result = await response.json();

    messageEl.style.color = response.ok ? 'green' : 'red';
    messageEl.textContent = result.message || result.error;
});

// Загрузка данных
document.getElementById('load-data').addEventListener('click', async () => {
    const messageEl = document.getElementById('data-message');
    const loadedDataEl = document.getElementById('loaded-data');

    const response = await fetch(`${API_URL}/user/data`, {
        method: 'GET',
        credentials: 'include'
    });

    if (!response.ok) {
        messageEl.style.color = 'red';
        messageEl.textContent = 'Ошибка загрузки данных';
        return;
    }

    const result = await response.json();
    loadedDataEl.textContent = JSON.stringify(result.data, null, 2);
    messageEl.style.color = 'green';
    messageEl.textContent = 'Данные загружены';
});

// Выход
document.getElementById('btn-logout').addEventListener('click', () => {
    // Просто перезагружаем страницу — сессия на сервере останется, но на клиенте "забудется"
    location.reload();
});