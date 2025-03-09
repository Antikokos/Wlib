from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Импортируем кастомную модель пользователя

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser  # Указываем кастомную модель
        fields = ('username', 'email', 'password1', 'password2')  # Поля для регистрации