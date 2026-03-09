from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.clinics.views import AuthViewSet

router = DefaultRouter()
router.register('', AuthViewSet, basename='auth')

urlpatterns = router.urls
