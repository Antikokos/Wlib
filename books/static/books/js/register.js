// Сообщения об ошибках
const ERROR_MESSAGES = {
    USERNAME: '3-30 символов (a-z, 0-9, _-)',
    EMAIL: 'Некорректный email',
    PASSWORD: '8-50 символов (A-Z, a-z, 0-9)',
    CONFIRM_PASSWORD: 'Пароли не совпадают'
};

// Получаем элементы формы
const form = document.getElementById('register-form');
const username = document.getElementById('username');
const email = document.getElementById('email');
const password = document.getElementById('password');
const confirmPassword = document.getElementById('confirm_password');

// Функция переключения видимости пароля
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// Обработчик социальной авторизации
function handleSocialAuth(provider) {
    console.log(`Авторизация через ${provider}`);
    alert(`Перенаправление на ${provider}...`);
}

// Валидация полей
function validateUsername(value) {
    return /^[a-z0-9_-]{3,30}$/i.test(value);
}

function validateEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function validatePassword(value) {
    return /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,50}$/.test(value);
}

// Установка/очистка ошибки
function setError(input, message = '') {
    const group = input.closest('.input-group');
    if (!group) return;

    group.classList.toggle('error', !!message);
    const errorEl = group.querySelector('.error-message');
    if (errorEl) errorEl.textContent = message;
}

// Обработчик отправки формы
function handleSubmit(e) {
    e.preventDefault();
    let isValid = true;

    // Очищаем все ошибки перед проверкой
    setError(username);
    setError(email);
    setError(password);
    setError(confirmPassword);

    // Проверяем поля
    if (!validateUsername(username.value.trim())) {
        setError(username, ERROR_MESSAGES.USERNAME);
        isValid = false;
    }

    if (!validateEmail(email.value.trim())) {
        setError(email, ERROR_MESSAGES.EMAIL);
        isValid = false;
    }

    if (!validatePassword(password.value.trim())) {
        setError(password, ERROR_MESSAGES.PASSWORD);
        isValid = false;
    }

    if (password.value !== confirmPassword.value) {
        setError(confirmPassword, ERROR_MESSAGES.CONFIRM_PASSWORD);
        isValid = false;
    }

    // Если форма валидна - отправляем
    if (isValid) {
        console.log('Форма готова к отправке:', {
            username: username.value,
            email: email.value
        });
        alert('Регистрация успешна!');
    } else {
        // Фокус на первое поле с ошибкой
        document.querySelector('.input-group.error input')?.focus();
    }
}

// Валидация в реальном времени
function setupLiveValidation() {
    username.addEventListener('input', () => {
        setError(username, username.value.trim() && !validateUsername(username.value.trim())
            ? ERROR_MESSAGES.USERNAME : '');
    });

    email.addEventListener('input', () => {
        setError(email, email.value.trim() && !validateEmail(email.value.trim())
            ? ERROR_MESSAGES.EMAIL : '');
    });

    password.addEventListener('input', () => {
        setError(password, password.value.trim() && !validatePassword(password.value.trim())
            ? ERROR_MESSAGES.PASSWORD : '');

        // Проверяем подтверждение пароля, если оно уже введено
        if (confirmPassword.value.trim()) {
            setError(confirmPassword, password.value !== confirmPassword.value
                ? ERROR_MESSAGES.CONFIRM_PASSWORD : '');
        }
    });

    confirmPassword.addEventListener('input', () => {
        setError(confirmPassword, confirmPassword.value.trim() && password.value !== confirmPassword.value
            ? ERROR_MESSAGES.CONFIRM_PASSWORD : '');
    });
}

// Инициализация
if (form) {
    form.addEventListener('submit', handleSubmit);
    setupLiveValidation();

    // Добавляем обработчики на кнопки "глазиков"
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', function () {
            const inputId = this.getAttribute('data-target');
            togglePasswordVisibility(inputId);
        });
    });
}