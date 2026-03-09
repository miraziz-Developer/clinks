from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.patients.views import PatientViewSet, MedicalRecordViewSet, GlobalPatientViewSet, ensure_in_clinic

router = DefaultRouter()
router.register('global', GlobalPatientViewSet, basename='global-patient')
router.register('', PatientViewSet, basename='patient')

urlpatterns = [
    path('ensure_in_clinic/', ensure_in_clinic, name='ensure_in_clinic'),
    path('', include(router.urls)),
    path('<uuid:patient_pk>/records/', MedicalRecordViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='patient-records'),
    path('<uuid:patient_pk>/records/<uuid:pk>/', MedicalRecordViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
    }), name='patient-record-detail'),
]
