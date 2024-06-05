"""
Serializers for review API.
"""
from rest_framework import serializers

from review.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for review."""

    class Meta:
        model = Review
        fields = ['property', 'user', 'rating', 'comment']
        read_only_fields = ['property', 'user']

    def validate_rating(self, value):
        """Check that the rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')

        return value