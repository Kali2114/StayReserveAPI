"""
Review models.
"""
from django.db import models
from django.conf import settings

from property.models import Property


class Review(models.Model):
    """Review object."""
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f'Review by {self.user} for {self.property}'
