"""
Properties models.
"""
from django.conf import settings
from django.db import models

from rest_framework.exceptions import ValidationError


class Property(models.Model):
    """Property object."""
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='property',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name
