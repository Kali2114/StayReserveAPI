"""
URL mappings for the reservation app.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from reservation import views


router = DefaultRouter()
router.register('reservations', views.ReservationViewSet)

app_name = 'reservation'

urlpatterns = [
    path('', include(router.urls))
]