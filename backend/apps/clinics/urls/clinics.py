from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.clinics.views import ClinicViewSet, ClinicServiceViewSet

router = DefaultRouter()
router.register('', ClinicViewSet, basename='clinic')

urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:clinic_pk>/services/', ClinicServiceViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='clinic-services'),
    path('<uuid:clinic_pk>/services/<uuid:pk>/', ClinicServiceViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='clinic-service-detail'),
]
