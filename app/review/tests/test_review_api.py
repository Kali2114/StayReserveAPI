"""
Tests for review API.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from property.models import Property
from review.models import Review
from review.serializers import ReviewSerializer


def property_reviews_url(property_id):
    """Create and return a review list URL for a specific property."""
    return reverse("property:property-reviews-list", args=[property_id])


def review_detail_url(property_id, review_id):
    """Create and return review detail URL for a specific property."""
    return reverse("property:property-reviews-detail", args=[property_id, review_id])


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


class PublicReviewApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving reviews."""
        res = self.client.get(property_reviews_url(1))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReviewApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.property = create_property(
            name="HIPHOPKEMP Hotel",
            location="Hradec Kralove",
            price=Decimal("5.69"),
            description="The largest Hip Hop festival in Europe.",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_reviews(self):
        """Test retrieving a list of reviews."""
        Review.objects.create(
            property=self.property, user=self.user, rating=5, comment="BOZKOV!"
        )
        Review.objects.create(
            property=self.property, user=self.user, rating=3, comment="Silla!"
        )
        url = property_reviews_url(self.property.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        reviews = Review.objects.all().order_by("-id")
        serializer = ReviewSerializer(reviews, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_reviews_limited_to_property(self):
        """Test list of reviews is limited to property."""
        property2 = create_property(
            name="IWASHA Hotel",
            location="Tokyo",
            price=Decimal("7.12"),
            description="Asian vibe.",
        )
        review1 = Review.objects.create(
            property=property2, user=self.user, rating=3, comment="Silla!"
        )
        review2 = Review.objects.create(
            property=self.property, user=self.user, rating=3, comment="Silla!"
        )
        url = property_reviews_url(self.property.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review = Review.objects.filter(property=self.property).order_by("-id")
        serializer = ReviewSerializer(review, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_partial_review_update(self):
        """Test partial update of review."""
        review = Review.objects.create(
            property=self.property, user=self.user, rating=3, comment="Silla!"
        )
        payload = {"comment": "Absolutely Amazing."}
        url = review_detail_url(self.property.id, review.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.comment, payload["comment"])

    def test_full_update_fails_for_read_only_fields(self):
        """Test that full update fails when trying to change read-only fields."""
        review = Review.objects.create(
            property=self.property, user=self.user, rating=3, comment="Silla!"
        )
        user2 = create_user(email="tes2@example.com", password="Test123")
        property2 = create_property(
            name="IWASHA Hotel",
            location="Tokyo",
            price=Decimal("7.12"),
            description="Asian vibe.",
        )
        payload = {
            "user": user2,
            "property": property2,
            "rating": 4,
            "comment": "New comment",
        }

        url = review_detail_url(self.property.id, review.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.property, self.property)
        self.assertEqual(review.user, self.user)

    def test_deleting_review(self):
        """Test deleting an review."""
        review = Review.objects.create(
            property=self.property, user=self.user, rating=3, comment="Silla!"
        )
        url = review_detail_url(self.property.id, review.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = Review.objects.filter(id=review.id).exists()
        self.assertFalse(exists)

    def test_create_review_successful(self):
        """Test creating a new review successful."""
        payload = {
            "property": self.property,
            "user": self.user,
            "rating": 4,
            "comment": "Test comment.",
        }
        url = property_reviews_url(self.property.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        reviews = Review.objects.filter(user=self.user).exists()
        self.assertTrue(reviews)

    def test_create_review_with_rating(self):
        """Test creating a new review with invalid rating fails."""
        payload = {
            "property": self.property,
            "user": self.user,
            "rating": -1,
            "comment": "Test comment.",
        }
        url = property_reviews_url(self.property.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        payload["rating"] = 6
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
