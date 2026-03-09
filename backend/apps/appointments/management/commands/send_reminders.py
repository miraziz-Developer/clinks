"""
Eslatmalar yuborish uchun management command
Usage: python manage.py send_reminders
Cron yoki Celery beat orqali har soatda ishlatiladi
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date, time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '24 soatlik eslatmalar yuborish'

    def handle(self, *args, **options):
        from apps.appointments.models import Appointment

        # Ertangi sanani olish
        tomorrow = timezone.now().date() + timedelta(days=1)

        appointments = Appointment.objects.filter(
            date=tomorrow,
            status__in=['pending', 'confirmed'],
            reminder_24h_sent=False,
        ).select_related('patient', 'doctor', 'clinic')

        sent_count = 0
        for appointment in appointments:
            try:
                from apps.bots.notifications import send_appointment_reminder
                send_appointment_reminder(appointment)
                appointment.reminder_24h_sent = True
                appointment.save(update_fields=['reminder_24h_sent'])
                sent_count += 1
            except Exception as e:
                logger.error(f"Eslatma yuborishda xato: {e}")

        self.stdout.write(
            self.style.SUCCESS(f'✅ {sent_count} ta eslatma yuborildi')
        )
