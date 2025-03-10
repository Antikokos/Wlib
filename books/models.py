from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    page_count = models.IntegerField()
    published_date = models.CharField(max_length=10)
    thumbnail = models.URLField()
    genre = models.CharField(max_length=50)  # Добавьте это поле

    def __str__(self):
        return self.title


from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Дополнительные поля, если нужно
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Указываем related_name для групп и разрешений
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Уникальное имя для обратной связи
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Уникальное имя для обратной связи
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )