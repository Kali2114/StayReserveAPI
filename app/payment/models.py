"""
Reservation models.
"""

from django.db import models

from reservation.models import Reservation


class Payment(models.Model):
    """Payment object."""

    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} for {self.reservation} by {self.reservation.user}, cost: {self.amount}"
