"""
Tests for payment API.
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from datetime import date

from reservation.models import Reservation
from property.models import Property
from payment.models import Payment
from payment.serializers import PaymentSerializer


def get_payment_url(reservation_id):
    """Generate URL for payment list for a specific reservation."""
    return reverse('reservation:reservation-payment-list', args=[reservation_id])

def create_user(email='test@example.com', password='Test123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

def create_property(owner, **kwargs):
    """Create and return a property."""
    default = {
        'name': 'Test name',
        'location': 'Location',
        'price': Decimal('2.29'),
        'description': 'Test description',
    }
    default.update(**kwargs)
    property = Property.objects.create(owner=owner, **default)

    return property

def create_reservation(property, user, **kwargs):
    """Create and return a reservation."""
    default = {
        'start_date': date.today(),
        'end_date': date.today(),
    }
    default.update(**kwargs)
    reservation = Reservation.objects.create(property=property, user=user, **default)

    return reservation

def create_payment(reservation=None, **kwargs):
    """Create and return a payment."""
    default = {
        'amount': 1200,
        'payment_method': 'PayPal',
    }
    default.update(**kwargs)
    payment = Payment.objects.create(reservation=reservation, **default)

    return payment

class PublicPaymentApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving payments."""
        reservation = create_reservation(
            property=create_property(
                owner=create_user(
                    email='test2@example.com')),
            user=create_user())
        url = get_payment_url(reservation.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePaymentApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.property = create_property(owner=self.user)
        self.reservation = create_reservation(property=self.property, user=self.user)

    def test_retrieving_payments(self):
        """Test retrieving a list of payments."""
        create_payment(reservation=self.reservation)
        create_payment(reservation=self.reservation)

        url = get_payment_url(self.reservation.id)
        res = self.client.get(url)
        payments = Payment.objects.all().order_by('-id')
        serializer = PaymentSerializer(payments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_payments_limited_to_user(self):
        """Test list of payments is limited to authenticated user."""
        other_user = create_user(email='test1@example.com')
        other_reservation = create_reservation(property=self.property, user=other_user)
        create_payment(reservation=other_reservation)
        create_payment(reservation=self.reservation)
        create_payment(reservation=self.reservation)

        url = get_payment_url(self.reservation.id)
        res = self.client.get(url)
        payments = Payment.objects.filter(reservation__user=self.user).order_by('-id')
        serializer = PaymentSerializer(payments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_partial_update_payment_method_not_allowed(self):
        """Test that partial updating a payment via PATCH method is not allowed."""
        create_payment(reservation=self.reservation)
        payload = {
            'amount': '600.00',
            'payment_method': 'Debit Card',
        }
        url = get_payment_url(self.reservation.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_full_update_payment_method_not_allowed(self):
        """Test that full updating a payment via PUT method is not allowed."""
        create_payment(reservation=self.reservation)
        other_reservation = create_reservation(property=self.property, user=self.user)
        payload = {
            'reservation': other_reservation,
            'amount': '600.00',
            'payment_method': 'Debit Card',
        }
        url = get_payment_url(self.reservation.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_method_not_allowed(self):
        """Test that delete payment is not allowed."""
        create_payment(reservation=self.reservation)
        url = get_payment_url(self.reservation.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_payment(self):
        """Test creating a payment successful."""
        payload = {
            'reservation': self.reservation.id,
            'amount': '4800.00',
            'payment_method': 'Credit Card',
        }
        url = get_payment_url(self.reservation.id)
        res = self.client.post(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Payment.objects.filter(reservation=payload['reservation']).exists()
        self.assertTrue(exists)

    def test_create_payment_negative_amount_error(self):
        """Test that creating a payment with invalid amount failed."""
        payload = {
            'reservation': self.reservation.id,
            'amount': 0,
            'payment_method': 'Credit Card',
        }
        url = get_payment_url(self.reservation.id)
        res = self.client.post(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        exists = Payment.objects.filter(reservation=payload['reservation']).exists()
        self.assertFalse(exists)

    def test_create_second_payment_for_reservation_fails(self):
        """Test that creating a second payment for the same reservation is not allowed."""
        create_payment(reservation=self.reservation)
        payload = {
            'reservation': self.reservation.id,
            'amount': '5300.00',
            'payment_method': 'Credit Card',
        }
        url = get_payment_url(self.reservation.id)
        res = self.client.post(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_payment_with_invalid_reservation(self):
        """Test creating a payment with an invalid reservation ID."""
        invalid_reservation_id = 99999
        payload = {
            'reservation': invalid_reservation_id,
            'amount': '50.00',
            'payment_method': 'Credit Card',
        }
        url = get_payment_url(invalid_reservation_id)
        res = self.client.post(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_payment_without_payment_method(self):
        """Test creating a payment without a payment method."""
        payload = {
            'reservation': self.reservation.id,
            'amount': '50.00',
        }
        url = get_payment_url(self.reservation.id)
        res = self.client.post(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('payment_method', res.data)

    def test_create_payment_without_amount(self):
        """Test creating a payment without an amount."""
        payload = {
            'reservation': self.reservation.id,
            'payment_method': 'Credit Card',
        }
        url = get_payment_url(self.reservation.id)
        res = self.client.post(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', res.data)
