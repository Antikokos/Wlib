from pathlib import Path
import os
from datetime import timedelta
from decouple import config, Csv
from django.conf.global_settings import STATICFILES_DIRS
from django.urls import reverse_lazy

# === Хелпер для обрезки кавычек из Railway ===
def get_env(key, default=None, cast=str):
    if cast == str:
        value = config(key, default=default)
        return value.strip('"').strip("'")
    return config(key, default=default, cast=cast)


# === Основная директория проекта ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Безопасность ===
SECRET_KEY = get_env('SECRET_KEY')
DEBUG = get_env('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = get_env('ALLOWED_HOSTS', cast=Csv())

# === Установленные приложения ===
INSTALLED_APPS = [
    'axes',
    'mathfilters',
    'mybooksite',
    'books.apps.BooksConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
]

# === Middleware ===
MIDDLEWARE = [
    'axes.middleware.AxesMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === URL и WSGI ===
ROOT_URLCONF = 'mybooksite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mybooksite.wsgi.application'

# === База данных ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env('DB_NAME'),
        'USER': get_env('DB_USER'),
        'PASSWORD': 'ftcOCOEDMMPNCEwU',
        'HOST': get_env('DB_HOST'),
        'PORT': get_env('DB_PORT'),
    }
}

# === Валидаторы паролей ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Язык и часовой пояс ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# === Статика ===
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'books/static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# === Primary Key поле по умолчанию ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === Редирект после входа ===
LOGIN_REDIRECT_URL = reverse_lazy('home')

# === Безопасность и HTTPS ===
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    "https://wlib-production.up.railway.app",
    "https://www.wlib-production.up.railway.app",
]

# === Отправка писем ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = get_env('DEFAULT_FROM_EMAIL', default='Wlib')

# === Axes настройки ===
AUTHENTICATION_BACKENDS = [ 
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=5)
AXES_RESET_ON_FAILURE = False
AXES_LOCKOUT_CALLABLE = 'books.utils.custom_lockout_response'
