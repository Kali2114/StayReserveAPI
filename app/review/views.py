"""
Views for review API.
"""
from rest_framework import viewsets

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from review import models, serializers
from property.models import Property


class ReviewViewSet(viewsets.ModelViewSet):
    """Manage review in the database."""
    serializer_class = serializers.ReviewSerializer
    queryset = models.Review.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve reviews for specific property."""
        property_id = self.kwargs['property_id']
        return self.queryset.filter(property_id=property_id).order_by('-id')

    def perform_create(self, serializer):
        """Create a new review."""
        property_id = self.kwargs['property_id']
        property = Property.objects.get(id=property_id)
        serializer.save(user=self.request.user, property=property)
