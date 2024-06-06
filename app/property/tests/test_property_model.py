"""
Tests for property model.
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from property import models


class PropertyModelTest(TestCase):
    """Test property models."""

    def test_create_properties(self):
        """Test creating property is successful."""
        user = get_user_model().objects.create(
            email="Test@example.com",
            password="Test123",
        )
        property = models.Property.objects.create(
            name="Warsaw Hotel",
            price=Decimal("3.5"),
            description="Test Description",
            owner=user,
        )

        self.assertEqual(str(property), property.name)
