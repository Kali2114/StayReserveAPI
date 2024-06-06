"""
Test for reservation model.
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from datetime import date

from reservation.models import Reservation
from property.models import Property


class ReservationModelTest(TestCase):
    """Test the reservation model."""

    def test_create_reservation(self):
        """Test creating a reservation is successful."""
        user = get_user_model().objects.create(
            email="Test@example.com",
            password="Test123",
        )
        property = Property.objects.create(
            name="Warsaw Hotel",
            price=Decimal("3.5"),
            description="Test Description",
            owner=user,
        )
        reservation = Reservation.objects.create(
            property=property,
            user=user,
            start_date=date.today(),
            end_date=date.today(),
        )

        self.assertEqual(str(reservation), f"Reservation by {user} for {property}")
