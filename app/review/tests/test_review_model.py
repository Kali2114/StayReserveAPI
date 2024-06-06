"""
Tests for review model.
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from property.models import Property
from review.models import Review


class ReviewModelTest(TestCase):
    """Test the review model."""

    def test_create_review(self):
        """Test creating a review is successful."""
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
        review = Review.objects.create(
            property=property, user=user, rating=5, comment="Best hotel ive ever been."
        )

        self.assertEqual(str(review), f"Review by {user} for {property}")
