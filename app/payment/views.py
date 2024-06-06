"""
Views for payment API.
"""

from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from reservation.models import Reservation
from payment import models, serializers


class PaymentViewSet(ModelViewSet):
    """View for manage payment APIs."""

    http_method_names = ["get", "post"]
    serializer_class = serializers.PaymentSerializer
    queryset = models.Payment.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve payments for authenticated user."""
        user = self.request.user
        return models.Payment.objects.filter(reservation__user=user).order_by("-id")

    def perform_create(self, serializer):
        """Create a new payment for a reservation linked to the authenticated user."""
        reservation_id = self.kwargs.get("reservation_id")
        reservation = get_object_or_404(
            Reservation, pk=reservation_id, user=self.request.user
        )
        serializer.save(reservation=reservation)
