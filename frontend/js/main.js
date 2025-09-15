console.log('main.js loaded successfully!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // Проверяем, что элементы существуют
    const btnRegister = document.getElementById('btn-register');
    const btnSubmitRegister = document.getElementById('submit-register');
    const btnLoginNav = document.getElementById('btn-login');
    const submitLogin = document.getElementById('submit-login');
    const btnLogout = document.getElementById('btn-logout');
    
    console.log('Register button:', btnRegister);
    console.log('Submit register button:', btnSubmitRegister);
    console.log('Login nav button:', btnLoginNav);
    console.log('Submit login button:', submitLogin);
    console.log('Logout button:', btnLogout);
    
    // Обработчики для кнопок навигации
    if (btnRegister) {
        btnRegister.addEventListener('click', function() {
            console.log('Register nav button clicked');
            document.getElementById('register-form').style.display = 'block';
            document.getElementById('login-form').style.display = 'none';
        });
    }
    
    if (btnLoginNav) {
        btnLoginNav.addEventListener('click', function() {
            console.log('Login nav button clicked');
            document.getElementById('login-form').style.display = 'block';
            document.getElementById('register-form').style.display = 'none';
        });
    }
    
    // Обработчики для кнопок форм
    if (btnSubmitRegister) {
        btnSubmitRegister.addEventListener('click', registerUser);
    }
    
    if (submitLogin) {
        submitLogin.addEventListener('click', loginUser);
    }
    
    if (btnLogout) {
        btnLogout.addEventListener('click', logoutUser);
    }
    
    checkAuthStatus();
});

// Функция регистрации
async function registerUser() {
    console.log('registerUser function called');
    
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const messageEl = document.getElementById('reg-message');
    
    console.log('Registration data:', { username, email, password: '***' });
    
    if (!username || !email || !password) {
        messageEl.textContent = 'Все поля обязательны для заполнения';
        messageEl.style.color = 'red';
        return;
    }
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, email, password })
        });
        
        console.log('Registration response status:', response.status);
        
        const data = await response.json();
        console.log('Registration response data:', data);
        
        if (response.ok) {
            messageEl.textContent = 'Регистрация успешна! Проверьте email.';
            messageEl.style.color = 'green';
            
            // Очищаем форму
            document.getElementById('reg-username').value = '';
            document.getElementById('reg-email').value = '';
            document.getElementById('reg-password').value = '';
            
        } else {
            messageEl.textContent = data.error || 'Ошибка регистрации';
            messageEl.style.color = 'red';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        messageEl.textContent = 'Сетевая ошибка: ' + error.message;
        messageEl.style.color = 'red';
    }
}

// Функция входа
async function loginUser() {
    console.log('loginUser function called');
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const messageEl = document.getElementById('login-message');
    
    console.log('Login data:', { email, password: '***' });
    
    if (!email || !password) {
        messageEl.textContent = 'Email и пароль обязательны';
        messageEl.style.color = 'red';
        return;
    }
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        console.log('Login response status:', response.status);
        
        const data = await response.json();
        console.log('Login response data:', data);
        
        if (response.ok) {
            messageEl.textContent = 'Вход успешен!';
            messageEl.style.color = 'green';
            
            // Очищаем форму
            document.getElementById('login-email').value = '';
            document.getElementById('login-password').value = '';
            
            checkAuthStatus();
        } else {
            messageEl.textContent = data.error || 'Ошибка входа';
            messageEl.style.color = 'red';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        messageEl.textContent = 'Сетевая ошибка: ' + error.message;
        messageEl.style.color = 'red';
    }
}

// Проверка статуса авторизации
async function checkAuthStatus() {
    console.log('checkAuthStatus called');
    
    try {
        const response = await fetch('/api/user/profile', {
            credentials: 'include'
        });
        
        console.log('Auth check response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('User data:', data);
            
            document.getElementById('welcome-username').textContent = data.username;
            document.getElementById('welcome-message').style.display = 'block';
            document.getElementById('btn-logout').style.display = 'inline-block';
            document.getElementById('btn-register').style.display = 'none';
            document.getElementById('btn-login').style.display = 'none';
            
        } else {
            console.log('User not authenticated');
            document.getElementById('welcome-message').style.display = 'none';
            document.getElementById('btn-logout').style.display = 'none';
            document.getElementById('btn-register').style.display = 'inline-block';
            document.getElementById('btn-login').style.display = 'inline-block';
        }
    } catch (error) {
        console.error('Ошибка проверки авторизации:', error);
    }
}

// Выход
async function logoutUser() {
    console.log('logoutUser called');
    
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        console.log('Logout response status:', response.status);
        
        if (response.ok) {
            checkAuthStatus();
        }
    } catch (error) {
        console.error('Ошибка выхода:', error);
    }
}