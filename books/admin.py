from django.contrib import admin
from .models import (
    UserProfile,
    UserBook,
    NewGenre,
    NewBook,
    NewUserBook
)

# Настройка отображения для модели UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_confirmed', 'confirmation_token')
    search_fields = ('user__username', 'user__email')

# Настройка отображения для модели UserBook
@admin.register(UserBook)
class UserBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'book_id', 'status', 'progress')
    list_filter = ('status',)
    search_fields = ('user__username', 'book_id')

# Настройка отображения для модели NewGenre
@admin.register(NewGenre)
class NewGenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}  # Автоматическое заполнение slug на основе name

# Настройка отображения для модели NewBook
@admin.register(NewBook)
class NewBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'published_date', 'language', 'average_rating', 'ratings_count')
    list_filter = ('genres', 'language', 'published_date')
    search_fields = ('title', 'authors', 'isbn_10', 'isbn_13')
    filter_horizontal = ('genres',)  # Удобный виджет для выбора жанров
    readonly_fields = ('created_at', 'updated_at')  # Поля только для чтения

# Настройка отображения для модели NewUserBook
@admin.register(NewUserBook)
class NewUserBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'progress', 'rating', 'date_added')
    list_filter = ('status', 'date_added', 'last_updated')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('date_added', 'last_updated')  # Поля только для чтения