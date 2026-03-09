from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import JsonResponse
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.clinics.urls.auth')),
        path('clinics/', include('apps.clinics.urls.clinics')),
        path('doctors/', include('apps.doctors.urls')),
        path('patients/', include('apps.patients.urls')),
        path('appointments/', include('apps.appointments.urls')),
        path('bots/', include('apps.bots.urls')),
        path('analytics/', include('apps.analytics.urls')),
        path('health/', lambda r: JsonResponse({'status': 'ok'})),
    ])),

    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Bot webhook
    path('webhook/', include('apps.bots.webhook_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
