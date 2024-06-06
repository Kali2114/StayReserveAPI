"""
Tests for reservation API.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from datetime import date, timedelta

from property.models import Property
from reservation.models import Reservation
from reservation.serializers import ReservationSerializer


RESERVATION_URL = reverse("reservation:reservation-list")


def detail_url(reservation_id):
    """Create and return reservation detail url."""
    return reverse("reservation:reservation-detail", args=[reservation_id])


def create_user(email="test@example.com", password="Test123"):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_property(name, location, price, description):
    """Create and return a property."""
    return Property.objects.create(
        name=name,
        location=location,
        price=price,
        description=description,
    )


class PublicReservationApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving reservations."""
        res = self.client.get(RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReservationApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.property = create_property(
            name="Kamileg Hotel",
            location="Warsaw",
            price=Decimal("1.5"),
            description="Best of the best",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_reservations(self):
        """Test retrieving a list of reservation."""
        Reservation.objects.create(
            user=self.user,
            property=self.property,
            start_date=date.today(),
            end_date=date.today(),
        )

        res = self.client.get(RESERVATION_URL)

        reservation = Reservation.objects.all().order_by("start_date")
        serializer = ReservationSerializer(reservation, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_reservations_limited_to_user(self):
        """Test list of reservations is limited to authenticated user."""
        user2 = create_user(email="test2@example.com")
        Reservation.objects.create(
            user=user2,
            property=self.property,
            start_date=date.today(),
            end_date=date.today(),
        )
        Reservation.objects.create(
            user=self.user,
            property=self.property,
            start_date=date.today(),
            end_date=date.today(),
        )
        res = self.client.get(RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_reservation_add_owner(self):
        """Test creating reservation automatically adds the logged-in user as the owner."""
        payload = {
            "property": self.property.id,
            "start_date": date.today(),
            "end_date": date.today(),
        }
        res = self.client.post(RESERVATION_URL, payload)
        reservation = Reservation.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reservation.user, self.user)

    def test_create_reservation_invalid_date(self):
        """Test creating reservation with invalid dates raises error."""
        property = Property.objects.create(
            name="Warsaw Hotel",
            price=Decimal("3.5"),
            description="Test Description",
        )
        payload = {
            "property": property.id,
            "start_date": date.today() + timedelta(days=1),
            "end_date": date.today(),
        }
        res = self.client.post(RESERVATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)
        self.assertEqual(
            res.data["non_field_errors"][0], "End date must be after start date."
        )

    def test_delete_reservation(self):
        """Test deleting a reservation."""
        reservation = Reservation.objects.create(
            user=self.user,
            property=self.property,
            start_date=date.today(),
            end_date=date.today(),
        )
        url = detail_url(reservation.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = Reservation.objects.filter(id=reservation.id).exists()
        self.assertFalse(exists)
