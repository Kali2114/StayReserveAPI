"""
URL mappings for the property app.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from property import views


router = DefaultRouter()
router.register('properties', views.PropertyViewSet)
router.register

app_name = 'property'

urlpatterns = [
    path('', include(router.urls))
]