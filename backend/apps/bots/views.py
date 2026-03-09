from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.bots.models import TelegramBot, BotUser
from apps.clinics.models import Clinic


class TelegramBotViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TelegramBot.objects.all()
        return TelegramBot.objects.filter(clinic__owner=user)

    @action(detail=True, methods=['post'])
    def set_webhook(self, request, pk=None):
        """Webhook o'rnatish"""
        bot = self.get_object()
        from django.conf import settings
        import httpx

        webhook_url = f"{settings.DOMAIN}/webhook/{bot.id}/"
        try:
            resp = httpx.post(
                f"https://api.telegram.org/bot{bot.token}/setWebhook",
                json={'url': webhook_url}
            )
            if resp.json().get('ok'):
                bot.webhook_url = webhook_url
                bot.is_webhook_set = True
                bot.save()
                return Response({'status': 'webhook o\'rnatildi', 'url': webhook_url})
            return Response({'error': resp.json()}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'])
    def delete_webhook(self, request, pk=None):
        bot = self.get_object()
        import httpx
        httpx.post(f"https://api.telegram.org/bot{bot.token}/deleteWebhook")
        bot.is_webhook_set = False
        bot.webhook_url = ''
        bot.save()
        return Response({'status': 'webhook o\'chirildi'})

    @action(detail=True, methods=['post'])
    def send_broadcast(self, request, pk=None):
        """Barcha bot foydalanuvchilariga xabar yuborish"""
        bot = self.get_object()
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Xabar matni kerak'}, status=400)

        from apps.bots.notifications import send_telegram_message
        sent = 0
        failed = 0
        for user in bot.bot_users.filter(is_blocked=False):
            result = send_telegram_message(bot.token, user.telegram_id, message)
            if result:
                sent += 1
            else:
                failed += 1

        return Response({'sent': sent, 'failed': failed})

    @action(detail=False, methods=['post'])
    def create_for_clinic(self, request):
        """Klinika uchun bot yaratish"""
        clinic_id = request.data.get('clinic_id')
        token = request.data.get('token')

        if not clinic_id or not token:
            return Response({'error': 'clinic_id va token kerak'}, status=400)

        try:
            clinic = Clinic.objects.get(id=clinic_id, owner=request.user)
        except Clinic.DoesNotExist:
            return Response({'error': 'Klinika topilmadi'}, status=404)

        if hasattr(clinic, 'telegram_bot'):
            return Response({'error': 'Klinikada allaqachon bot bor'}, status=400)

        # Bot ma'lumotlarini tekshirish
        import httpx
        resp = httpx.get(f"https://api.telegram.org/bot{token}/getMe")
        bot_info = resp.json()
        if not bot_info.get('ok'):
            return Response({'error': 'Token noto\'g\'ri'}, status=400)

        bot_data = bot_info['result']
        bot = TelegramBot.objects.create(
            clinic=clinic,
            token=token,
            username=bot_data.get('username', ''),
            name=bot_data.get('first_name', ''),
        )
        return Response({
            'id': str(bot.id),
            'username': bot.username,
            'name': bot.name,
            'status': 'Bot yaratildi! Webhook o\'rnatish uchun /set_webhook endpoint\'ini ishlatng.',
        }, status=201)
