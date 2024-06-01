"""
Test for user models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTests(TestCase):
    """Test user models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'Test@example.com'
        password = 'Test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ('test@EXAMPLE.com', 'test@example.com'),
            ('Test@Example.COM', 'Test@example.com'),
            ('TEST@ExAmple.cOm', 'TEST@example.com'),
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='Test123',
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """Test raises ValueError when creating user without email."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='Test123',
            )

    def test_create_superuser(self):
        """Test creating a superuser successful."""
        user = get_user_model().objects.create_superuser(
            email='example@test.com',
            password='Test123',
        )


        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
