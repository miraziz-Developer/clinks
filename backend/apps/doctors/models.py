from django.db import models
from apps.base_models import TimeStampedModel
from apps.clinics.models import Clinic, ClinicService


class Doctor(TimeStampedModel):
    """Shifokor modeli"""

    clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE,
        related_name='doctors', verbose_name='Klinika'
    )

    # Shaxsiy ma'lumotlar
    first_name = models.CharField(max_length=100, verbose_name='Ism')
    last_name = models.CharField(max_length=100, verbose_name='Familiya')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    photo = models.ImageField(
        upload_to='doctor_photos/', null=True, blank=True, verbose_name='Foto'
    )

    # Professional ma'lumotlar
    specialty = models.CharField(max_length=255, verbose_name='Mutaxassislik')
    experience_years = models.PositiveIntegerField(default=0, verbose_name='Tajriba (yil)')
    bio = models.TextField(blank=True, verbose_name='Haqida')
    education = models.TextField(blank=True, verbose_name='Ta\'lim')
    achievements = models.TextField(blank=True, verbose_name='Yutuqlar')

    # Narx
    consultation_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='Konsultatsiya narxi (so\'m)'
    )

    # Xizmatlar
    services = models.ManyToManyField(
        ClinicService, blank=True,
        related_name='doctors', verbose_name='Xizmatlar'
    )

    # Ish vaqti (klinikadan farq qilishi mumkin)
    custom_schedule = models.BooleanField(default=False, verbose_name='Alohida jadval?')
    work_start = models.TimeField(null=True, blank=True)
    work_end = models.TimeField(null=True, blank=True)
    working_days = models.JSONField(
        null=True, blank=True,
        verbose_name='Ish kunlari (alohida)'
    )

    # Status
    is_active = models.BooleanField(default=True, verbose_name='Faolmi?')

    # Statistika
    total_appointments = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)

    class Meta:
        verbose_name = 'Shifokor'
        verbose_name_plural = 'Shifokorlar'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"Dr. {self.last_name} {self.first_name} — {self.specialty}"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}".strip()

    def get_effective_work_start(self):
        return self.work_start if self.custom_schedule else self.clinic.work_start

    def get_effective_work_end(self):
        return self.work_end if self.custom_schedule else self.clinic.work_end

    def get_effective_working_days(self):
        return self.working_days if self.custom_schedule else self.clinic.working_days

    def get_available_slots(self, date):
        """Berilgan sana uchun bo'sh vaqtlar"""
        from datetime import datetime, timedelta
        from django.utils import timezone

        work_start = self.get_effective_work_start()
        work_end = self.get_effective_work_end()
        duration = self.clinic.appointment_duration

        # Slot'larni yaratish
        slots = []
        current = datetime.combine(date, work_start)
        end = datetime.combine(date, work_end)

        # Tushlik vaqtini hisobga olish
        lunch_start = self.clinic.lunch_start
        lunch_end = self.clinic.lunch_end

        while current + timedelta(minutes=duration) <= end:
            slot_time = current.time()

            # Tushlikni o'tkazib yuborish
            if lunch_start and lunch_end:
                if lunch_start <= slot_time < lunch_end:
                    current += timedelta(minutes=duration)
                    continue

            slots.append(slot_time)
            current += timedelta(minutes=duration)

        # Band vaqtlarni olib tashlash
        booked_times = set(
            self.appointments.filter(
                date=date,
                status__in=['pending', 'confirmed']
            ).values_list('time', flat=True)
        )

        return [s for s in slots if s not in booked_times]


class DoctorScheduleException(TimeStampedModel):
    """Shifokor dam olish kunlari / ishlash vaqti istisnolari"""
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE,
        related_name='schedule_exceptions'
    )
    date = models.DateField()
    is_working = models.BooleanField(default=False)
    work_start = models.TimeField(null=True, blank=True)
    work_end = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Jadval istisnosi"
        verbose_name_plural = "Jadval istisno"
        unique_together = ['doctor', 'date']
