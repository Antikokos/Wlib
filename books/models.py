# models.py
from django.db import models
from django.contrib.auth.models import User

class UserBook(models.Model):
    STATUS_CHOICES = [
        ('reading', 'Читаю'),
        ('want-to-read', 'В планах'),
        ('read', 'Прочитано'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_id = models.CharField(max_length=255)  # ID книги из Google Books API
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    progress = models.PositiveIntegerField(default=0)  # Прогресс чтения в процентах
    

    class Meta:
        unique_together = ('user', 'book_id')  # Пользователь не может добавить одну книгу дважды

    def __str__(self):
        return f"{self.user.username} - {self.book_id} ({self.status})"
