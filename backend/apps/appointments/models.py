from django.db import models
from apps.base_models import TimeStampedModel
from apps.clinics.models import Clinic, ClinicService


class AppointmentStatus(models.TextChoices):
    PENDING = 'pending', '⏳ Kutilmoqda'
    CONFIRMED = 'confirmed', '✅ Tasdiqlangan'
    CANCELLED = 'cancelled', '❌ Bekor qilingan'
    COMPLETED = 'completed', '✔️ Tugallangan'
    NO_SHOW = 'no_show', '👻 Kelmadi'
    RESCHEDULED = 'rescheduled', '🔄 Ko\'chirilgan'


class Appointment(TimeStampedModel):
    """Navbat modeli"""

    clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE,
        related_name='appointments', verbose_name='Klinika'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor', on_delete=models.CASCADE,
        related_name='appointments', verbose_name='Shifokor'
    )
    patient = models.ForeignKey(
        'patients.Patient', on_delete=models.CASCADE,
        related_name='appointments', verbose_name='Bemor'
    )
    service = models.ForeignKey(
        ClinicService, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='appointments', verbose_name='Xizmat'
    )

    # Vaqt
    date = models.DateField(verbose_name='Sana')
    time = models.TimeField(verbose_name='Vaqt')
    duration = models.PositiveIntegerField(
        default=30, verbose_name='Davomiyligi (daqiqa)'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        verbose_name='Status'
    )

    # Ma'lumotlar
    complaint = models.TextField(blank=True, verbose_name='Shikoyat')
    notes = models.TextField(blank=True, verbose_name='Izohlar')

    # To'lov
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='Narxi (so\'m)'
    )
    is_paid = models.BooleanField(default=False, verbose_name='To\'langanmi?')

    # Telegram
    telegram_message_id = models.BigIntegerField(
        null=True, blank=True,
        verbose_name='Telegram xabar ID'
    )
    reminder_sent = models.BooleanField(default=False)
    reminder_24h_sent = models.BooleanField(default=False)

    # Bekor qilish sababi
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.CharField(
        max_length=20,
        choices=[('patient', 'Bemor'), ('clinic', 'Klinika'), ('system', 'Tizim')],
        blank=True
    )

    class Meta:
        verbose_name = 'Navbat'
        verbose_name_plural = 'Navbatlar'
        ordering = ['-date', '-time']
        unique_together = [['doctor', 'date', 'time']]

    def __str__(self):
        return f"{self.patient.full_name} → Dr.{self.doctor.last_name} | {self.date} {self.time}"

    def confirm(self):
        self.status = AppointmentStatus.CONFIRMED
        self.save()
        self._send_confirmation_notification()

    def cancel(self, reason='', cancelled_by='system'):
        self.status = AppointmentStatus.CANCELLED
        self.cancellation_reason = reason
        self.cancelled_by = cancelled_by
        self.save()
        self._send_cancellation_notification()

    def complete(self):
        self.status = AppointmentStatus.COMPLETED
        self.save()
        # Statistika yangilash
        patient = self.patient
        patient.total_visits += 1
        patient.last_visit = self.date
        patient.save()
        doctor = self.doctor
        doctor.total_appointments += 1
        doctor.save()
        clinic = self.clinic
        clinic.total_appointments += 1
        clinic.save()

    def _send_confirmation_notification(self):
        """Telegram orqali tasdiqlash xabari"""
        try:
            from apps.bots.notifications import send_appointment_confirmation
            send_appointment_confirmation(self)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Notification error: {e}")

    def _send_cancellation_notification(self):
        """Telegram orqali bekor qilish xabari"""
        try:
            from apps.bots.notifications import send_appointment_cancellation
            send_appointment_cancellation(self)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Notification error: {e}")

    @property
    def end_time(self):
        from datetime import datetime, timedelta
        end_dt = datetime.combine(self.date, self.time) + timedelta(minutes=self.duration)
        return end_dt.time()
