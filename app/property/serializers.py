"""
Serializers for property API View.
"""

from rest_framework import serializers

from property.models import Property
from reservation.serializers import ReservationSerializer
from review.serializers import ReviewSerializer


class PropertySerializer(serializers.ModelSerializer):
    """Serializer for property."""

    class Meta:
        model = Property
        fields = ["id", "name", "location", "price", "owner"]
        read_only_fields = ["id"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class PropertyDetailSerializer(PropertySerializer):
    """Serializer for detail property."""

    reservations = ReservationSerializer(
        many=True, read_only=True, source="reservation"
    )
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta(PropertySerializer.Meta):
        fields = PropertySerializer.Meta.fields + [
            "description",
            "reservations",
            "reviews",
        ]
