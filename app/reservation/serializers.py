"""
Serializers for reservation API View.
"""
from rest_framework import serializers

from reservation.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for reservations."""

    class Meta:
        model = Reservation
        fields = ['id', 'property', 'user', 'start_date', 'end_date']
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        """Validate that start date is before end date."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date > end_date:
            raise serializers.ValidationError('End date must be after start date.')

        return attrs
