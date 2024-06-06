"""
Tests for payment model.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from datetime import date

from property.models import Property
from reservation.models import Reservation
from payment.models import Payment


class PaymentModelTest(TestCase):
    """Test the payment model."""

    def test_create_payment(self):
        """Test creating a payment is successful."""
        user = get_user_model().objects.create_user(
            email='Test@example.com',
            password="Test123"
        )
        property = Property.objects.create(
            name='Warsaw Hotel',
            price=Decimal('3.5'),
            description='Test Description',
            owner=user
        )
        reservation = Reservation.objects.create(
            property=property,
            user=user,
            start_date=date.today(),
            end_date=date.today(),
        )
        payment = Payment.objects.create(
            reservation=reservation,
            amount=225.50,
            payment_method='PayPal'
        )

        self.assertEqual(str(payment), f'{payment.pk} for {reservation} by {reservation.user}, cost: {payment.amount}')