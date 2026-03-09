from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.appointments.views import AppointmentViewSet

router = DefaultRouter()
router.register('', AppointmentViewSet, basename='appointment')

urlpatterns = router.urls
