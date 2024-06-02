"""
Views for property API.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from property import models, serializers


class PropertyViewSet(viewsets.ModelViewSet):
    """View for manage property APIs."""
    serializer_class = serializers.PropertyDetailSerializer
    queryset = models.Property.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve properties for authenticated user."""
        user = self.request.user
        return (models.Property.objects.filter(owner=user) |
                models.Property.objects.filter(owner__isnull=True)).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.PropertySerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new property."""
        serializer.save()
