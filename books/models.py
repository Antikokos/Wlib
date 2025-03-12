from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    page_count = models.IntegerField(blank=True, null=True)
    published_date = models.IntegerField(blank=True, null=True)
    thumbnail = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
