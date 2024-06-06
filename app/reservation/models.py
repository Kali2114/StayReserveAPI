"""
Reservations models.
"""

from django.db import models
from django.conf import settings

from property.models import Property


class Reservation(models.Model):
    """Reservation object."""

    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Reservation by {self.user} for {self.property}"
