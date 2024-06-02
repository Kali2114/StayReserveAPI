"""
Tests for property API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from property.models import Property

from property.serializers import (
    PropertySerializer,
    PropertyDetailSerializer,
)


PROPERTY_URL = reverse('property:property-list')


def detail_url(property_id):
    """Create and return a property detail URL."""
    return reverse('property:property-detail', args=[property_id])

def create_property(owner=None, **kwargs):
    default = {
        'name': 'test name',
        'location': 'test location',
        'price': Decimal('3.5'),
        'description': 'test description'
    }
    default.update(**kwargs)

    property = Property.objects.create(owner=owner, **default)
    return property

class PublicPropertyAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(PROPERTY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePropertiesAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='Test123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_properties(self):
        """Test retrieving a list of property."""
        create_property(owner=self.user)
        create_property(owner=self.user)

        res = self.client.get(PROPERTY_URL)

        properties = Property.objects.all().order_by('-id')
        serializer = PropertySerializer(properties, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_property_list_limited_to_user(self):
        """Test list of property is limited to authenticated user."""
        another_user = get_user_model().objects.create_user(
            email='another@example.com',
            password='Test123',
        )
        create_property(owner=self.user, name='property1')
        create_property(owner=self.user, name='property2')
        create_property(owner=another_user, name='another')

        res = self.client.get(PROPERTY_URL)

        properties = Property.objects.filter(owner=self.user).order_by('-id')
        serializer = PropertySerializer(properties, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_properties_for_user_including_unassigned(self):
        """Test retrieving properties for authenticated user including unassigned properties."""
        another_user = get_user_model().objects.create_user(
            email='another@example.com',
            password='Test123',
        )
        create_property(owner=self.user, name='property1')
        create_property(owner=self.user, name='property2')
        create_property(owner=another_user, name='another')
        create_property(name='empty1')
        create_property(name='empty1')

        res = self.client.get(PROPERTY_URL)

        properties = (Property.objects.filter(owner=self.user) |
                      Property.objects.filter(owner__isnull=True).order_by('-id'))
        serializer = PropertySerializer(properties, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 4)

    def test_get_property_detail(self):
        """Test get property details."""
        property = create_property(owner=self.user)
        url = detail_url(property.id)

        res = self.client.get(url)
        serializer = PropertyDetailSerializer(property)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_property(self):
        """Test creating a property."""
        payload = {
            'name': 'Barcelona Hotel',
            'location': 'Spain, Barcelona',
            'price': Decimal('3.5'),
            'description': 'FC BARCELONA',
        }
        res = self.client.post(PROPERTY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        property = Property.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(property, k), v)

    def test_create_property_with_wrong_price(self):
        """Test creating property with zero price raises error."""
        payload = {
            'name': 'Free Hotel',
            'location': 'Some Location',
            'price': Decimal('0.00'),
            'description': 'Some Description',
        }
        res = self.client.post(PROPERTY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', res.data)

    def test_partial_update(self):
        """Test partial update of the property."""
        property = create_property(
            name='Warsaw Hotel',
            location='Warsaw, Poland',
            price=Decimal('5.5'),
            description='Best Warsaw hotel.',
            owner=self.user,
        )
        payload = {'description': 'Almost best hotel in Warsaw.'}

        url = detail_url(property.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        property.refresh_from_db()
        self.assertEqual(property.description, payload['description'])
        self.assertEqual(property.owner, self.user)

    def test_full_update(self):
        """Test full update of property."""
        property = create_property(
            name='Warsaw Hotel',
            location='Warsaw, Poland',
            price=Decimal('5.5'),
            description='Best Warsaw hotel.',
        )
        payload = {
            'name': 'Barcelona Hotel',
            'location': 'Barcelona, Spain',
            'price': Decimal('9.5'),
            'description': 'FORZA BARCA!',
            'owner': self.user.id
        }

        url = detail_url(property.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        property.refresh_from_db()
        for k, v in payload.items():
            if k == 'owner':
                self.assertEqual(property.owner.id, v)
            else:
                self.assertEqual(getattr(property, k), v)

    def test_delete_property(self):
        """Test deleting a property successful."""
        property = create_property()

        url = detail_url(property.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Property.objects.filter(id=property.id).exists())

    def test_delete_another_users_property_error(self):
        """Test trying to delete another users property gives error."""
        another_user = get_user_model().objects.create_user(
            email='another@example.com',
            password='Another123',
            name='Another',
        )
        property = create_property(owner=another_user)

        url = detail_url(property.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Property.objects.filter(id=property.id).exists())
