from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.doctors.views import DoctorViewSet

router = DefaultRouter()
router.register('', DoctorViewSet, basename='doctor')

urlpatterns = router.urls
