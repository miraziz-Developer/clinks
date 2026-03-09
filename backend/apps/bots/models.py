from django.db import models
from apps.base_models import TimeStampedModel
from apps.clinics.models import Clinic


class TelegramBot(TimeStampedModel):
    """Klinikaga biriktirilgan Telegram bot"""
    clinic = models.OneToOneField(
        Clinic, on_delete=models.CASCADE,
        related_name='telegram_bot', verbose_name='Klinika'
    )
    token = models.CharField(max_length=100, unique=True, verbose_name='Bot token')
    username = models.CharField(max_length=100, blank=True, verbose_name='Bot username')
    name = models.CharField(max_length=255, blank=True, verbose_name='Bot nomi')

    # Webhook
    webhook_url = models.URLField(blank=True)
    is_webhook_set = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(default=True, verbose_name='Faolmi?')

    # Sozlamalar
    welcome_message = models.TextField(
        default='Assalomu alaykum! {clinic_name} klinikasiga xush kelibsiz! 🏥\n\n'
                'Navbat olish uchun /start buyrug\'ini yuboring.',
        verbose_name='Xush kelibsiz xabari'
    )
    language = models.CharField(
        max_length=5, default='uz',
        choices=[('uz', "O'zbek"), ('ru', 'Русский')],
        verbose_name='Til'
    )

    # Statistika
    total_users = models.PositiveIntegerField(default=0)
    total_appointments_via_bot = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Telegram Bot'
        verbose_name_plural = 'Telegram Botlar'

    def __str__(self):
        return f"@{self.username} → {self.clinic.name}"


class BotUser(TimeStampedModel):
    """Bot foydalanuvchisi (Telegram orqali ro'yxatdan o'tgan bemor)"""
    bot = models.ForeignKey(
        TelegramBot, on_delete=models.CASCADE,
        related_name='bot_users', verbose_name='Bot'
    )
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID')
    telegram_username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    language = models.CharField(max_length=5, default='uz')

    # Bog'liq bemor
    patient = models.ForeignKey(
        'patients.Patient', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='bot_users'
    )

    # Bot holati (FSM)
    state = models.CharField(max_length=100, blank=True, default='')
    state_data = models.JSONField(default=dict)

    is_blocked = models.BooleanField(default=False)
    last_interaction = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bot foydalanuvchisi'
        verbose_name_plural = 'Bot foydalanuvchilari'
        unique_together = [['bot', 'telegram_id']]

    def __str__(self):
        return f"@{self.telegram_username or self.telegram_id} ({self.bot.clinic.name})"


class BotMessage(TimeStampedModel):
    """Yuborilgan xabarlar logi"""
    bot = models.ForeignKey(TelegramBot, on_delete=models.CASCADE)
    bot_user = models.ForeignKey(BotUser, on_delete=models.CASCADE, null=True)
    telegram_id = models.BigIntegerField()
    message_type = models.CharField(max_length=50, default='text')
    content = models.TextField()
    direction = models.CharField(
        max_length=10,
        choices=[('in', 'Kiruvchi'), ('out', 'Chiquvchi')],
        default='out'
    )
    message_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'
        ordering = ['-created_at']
