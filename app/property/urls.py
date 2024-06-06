"""
URL mappings for the property app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from property.views import PropertyViewSet
from review.views import ReviewViewSet

router = DefaultRouter()
router.register("properties", PropertyViewSet)
router.register(
    r"properties/(?P<property_id>\d+)/reviews",
    ReviewViewSet,
    basename="property-reviews",
)

app_name = "property"

urlpatterns = [path("", include(router.urls))]
