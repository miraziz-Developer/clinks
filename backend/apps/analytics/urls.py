from django.urls import path
from apps.analytics.views import ClinicAnalyticsView, SuperAdminAnalyticsView

urlpatterns = [
    path('clinic/', ClinicAnalyticsView.as_view(), name='clinic-analytics'),
    path('super/', SuperAdminAnalyticsView.as_view(), name='super-analytics'),
]
