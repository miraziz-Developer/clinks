from django.contrib import admin
from django.utils.html import format_html
from apps.bots.models import TelegramBot, BotUser, BotMessage


@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = [
        'bot_link', 'clinic', 'is_active', 'webhook_status',
        'total_users', 'total_appointments_via_bot', 'created_at'
    ]
    list_filter = ['is_active', 'is_webhook_set', 'language']
    readonly_fields = ['id', 'webhook_url', 'is_webhook_set', 'total_users',
                       'total_appointments_via_bot', 'created_at']

    def bot_link(self, obj):
        if obj.username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank">@{}</a>',
                obj.username, obj.username
            )
        return obj.token[:20] + '...'
    bot_link.short_description = 'Bot'

    def webhook_status(self, obj):
        if obj.is_webhook_set:
            return format_html(
                '<span style="color:green">✅ O\'rnatilgan</span>'
            )
        return format_html('<span style="color:red">❌ O\'rnatilmagan</span>')
    webhook_status.short_description = 'Webhook'


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = [
        'telegram_id', 'first_name', 'last_name', 'phone',
        'bot', 'language', 'is_blocked', 'last_interaction'
    ]
    list_filter = ['language', 'is_blocked', 'bot']
    search_fields = ['first_name', 'last_name', 'phone', 'telegram_username']
    readonly_fields = ['id', 'created_at', 'last_interaction']
