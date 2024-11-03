from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Snippet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    snippet = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)

    