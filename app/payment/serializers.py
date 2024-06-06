"""
Serializers for payment API view.
"""

from decimal import Decimal

from rest_framework import serializers

from payment.models import Payment
from reservation.models import Reservation


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment."""

    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reservation = serializers.PrimaryKeyRelatedField(queryset=Reservation.objects.all())

    class Meta:
        model = Payment
        fields = ["id", "reservation", "amount", "payment_method", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")

        return value

    def validate_reservation(self, value):
        if Payment.objects.filter(reservation=value).exists():
            raise serializers.ValidationError(
                "There is already a payment for this reservation."
            )
        return value
