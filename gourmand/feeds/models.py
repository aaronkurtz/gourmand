from django.db import models


class Feed(models.Model):
    href = models.URLField(max_length=2048, unique=True, verbose_name="HREF")
    link = models.URLField(max_length=2048, blank=True)
    title = models.TextField()

    def __str__(self):
        return self.title
