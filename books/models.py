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
