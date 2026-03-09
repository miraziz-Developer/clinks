from django.urls import path
from django.views import View
from django.http import JsonResponse
import json
import logging

logger = logging.getLogger(__name__)


class BotWebhookView(View):
    """Telegram webhook endpoint"""

    def post(self, request, bot_id):
        try:
            from apps.bots.models import TelegramBot
            bot = TelegramBot.objects.select_related('clinic').get(id=bot_id, is_active=True)
        except Exception:
            return JsonResponse({'error': 'Bot topilmadi'}, status=404)

        try:
            data = json.loads(request.body)
            # Bot handler'ga uzatish
            from apps.bots.handlers import handle_update
            handle_update(bot, data)
        except Exception as e:
            logger.error(f"Webhook error for bot {bot_id}: {e}")

        return JsonResponse({'ok': True})


urlpatterns = [
    path('<uuid:bot_id>/', BotWebhookView.as_view(), name='bot-webhook'),
]
