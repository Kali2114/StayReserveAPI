"""
URL mappings for the reservation app.
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from payment.views import PaymentViewSet
from reservation import views


router = DefaultRouter()
router.register("reservations", views.ReservationViewSet)
router.register(
    r"reservations/(?P<reservation_id>\d+)/payments",
    PaymentViewSet,
    basename="reservation-payment",
)

app_name = "reservation"

urlpatterns = [path("", include(router.urls))]
