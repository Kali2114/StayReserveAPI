"""
Filters for property API.
"""
from django_filters import rest_framework as filters

from property.models import Property


class PropertyFilter(filters.FilterSet):
    """Filter class for propery queryset."""
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Property
        fields = ['name', 'location', 'price']