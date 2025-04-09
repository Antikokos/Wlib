from django.db import models
from django.contrib.auth.models import User
import uuid

# Старые модели (оставляем без изменений для совместимости)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class UserBook(models.Model):
    STATUS_CHOICES = [
        ('reading', 'Читаю'),
        ('want-to-read', 'В планах'),
        ('read', 'Прочитано'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    progress = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'book_id')

    def __str__(self):
        return f"{self.user.username} - {self.book_id} ({self.status})"

# Новые модели (для будущего использования)
class NewGenre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название жанра")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    
    def __str__(self):
        return self.name

class NewBook(models.Model):
    # Основная информация
    title = models.CharField(max_length=255, verbose_name="Название")
    authors = models.CharField(max_length=255, verbose_name="Авторы")
    publisher = models.CharField(max_length=255, blank=True, null=True, verbose_name="Издательство")
    published_date = models.CharField(max_length=50, blank=True, null=True, verbose_name="Дата публикации")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    page_count = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество страниц")
    
    # Связи
    genres = models.ManyToManyField(NewGenre, related_name='books', verbose_name="Жанры")
    
    # Изображения
    thumbnail = models.URLField(max_length=500, blank=True, null=True, verbose_name="Обложка (URL)")
    small_thumbnail = models.URLField(max_length=500, blank=True, null=True, verbose_name="Миниатюра (URL)")
    
    # Идентификаторы
    google_books_id = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="ID Google Books")
    isbn_10 = models.CharField(max_length=10, blank=True, null=True, unique=True, verbose_name="ISBN-10")
    isbn_13 = models.CharField(max_length=13, blank=True, null=True, unique=True, verbose_name="ISBN-13")
    
    # Дополнительные поля
    language = models.CharField(max_length=10, default='ru', verbose_name="Язык")
    average_rating = models.FloatField(blank=True, null=True, verbose_name="Средний рейтинг")
    ratings_count = models.PositiveIntegerField(default=0, verbose_name="Количество оценок")
    
    # Системные поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return f"{self.title} - {self.authors}"

class NewUserBook(models.Model):
    STATUS_CHOICES = [
        ('reading', 'Читаю'),
        ('want-to-read', 'В планах'),
        ('read', 'Прочитано'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='new_user_books')
    book = models.ForeignKey(NewBook, on_delete=models.CASCADE, related_name='user_books')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    progress = models.PositiveIntegerField(default=0)
    rating = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Оценка (1-5)")
    review = models.TextField(blank=True, null=True, verbose_name="Рецензия")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"