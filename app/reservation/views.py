"""
Views for reservation API.
"""

from rest_framework import viewsets, mixins

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from reservation import models, serializers


class ReservationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Manage reservations in the database."""

    serializer_class = serializers.ReservationSerializer
    queryset = models.Reservation.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return (
            super().get_queryset().filter(user=self.request.user).order_by("start_date")
        )

    def perform_create(self, serializer):
        """Create a new reservation with the authenticated user as owner."""
        serializer.save(user=self.request.user)
