from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.bots.views import TelegramBotViewSet

router = DefaultRouter()
router.register('', TelegramBotViewSet, basename='telegrambot')

urlpatterns = router.urls
