# models.py
from django.db import models
from django.conf import settings


class Farm(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    size = models.FloatField(help_text="Size in acres",null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Connect farm to user
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farms'
    )

    def __str__(self):
        return f"{self.name} - {self.owner.email}"




