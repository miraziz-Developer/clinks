from django.db import models
from apps.base_models import TimeStampedModel
import uuid


class GlobalPatient(TimeStampedModel):
    """
    Platform-wide Patient (global).
    Bitta bemor barcha klinikalarda ishlatiladi.
    Telegram ID orqali taniladi.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Telegram info (asosiy identifikator)
    telegram_id = models.BigIntegerField(
        unique=True, verbose_name='Telegram ID'
    )
    telegram_username = models.CharField(
        max_length=100, blank=True, verbose_name='Telegram username'
    )
    telegram_first_name = models.CharField(
        max_length=100, blank=True, verbose_name='Telegram ism'
    )
    telegram_last_name = models.CharField(
        max_length=100, blank=True, verbose_name='Telegram familiya'
    )
    telegram_language = models.CharField(
        max_length=10, default='uz', verbose_name='Til sozlamasi'
    )
    telegram_phone = models.CharField(
        max_length=20, blank=True, verbose_name='Telefon (Telegramdan)'
    )

    # Profil (ixtiyoriy — user to'ldirsa)
    first_name = models.CharField(max_length=100, blank=True, verbose_name='Ism')
    last_name = models.CharField(max_length=100, blank=True, verbose_name='Familiya')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan sana")

    GENDER_CHOICES = [('male', '👨 Erkak'), ('female', '👩 Ayol'), ('unknown', '❓ Nomalum')]
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, default='unknown', verbose_name='Jins'
    )
    city = models.CharField(max_length=100, blank=True, verbose_name='Shahar')

    # Platform holati
    is_blocked = models.BooleanField(default=False, verbose_name='Bloklangan?')
    is_registered = models.BooleanField(
        default=False, verbose_name='Profil to\'ldirilgan?'
    )
    last_active = models.DateTimeField(null=True, blank=True, verbose_name='Oxirgi faollik')

    # Statistika
    total_appointments = models.PositiveIntegerField(default=0, verbose_name='Jami navbatlar')
    total_clinics_visited = models.PositiveIntegerField(default=0, verbose_name='Tashrif etgan klinikalar')

    class Meta:
        verbose_name = 'Bemor (Global)'
        verbose_name_plural = 'Bemorlar (Global)'
        ordering = ['-created_at']

    def __str__(self):
        name = self.display_name
        return f"{name} (TG: {self.telegram_id})"

    @property
    def display_name(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}".strip()
        if self.telegram_first_name:
            return f"{self.telegram_first_name} {self.telegram_last_name}".strip()
        return f"User {self.telegram_id}"

    @property
    def age(self):
        if self.date_of_birth:
            from django.utils import timezone
            return (timezone.now().date() - self.date_of_birth).days // 365
        return None

    @classmethod
    def get_or_create_from_telegram(cls, tg_user):
        """Telegram user ob'ektidan GlobalPatient olish yoki yaratish"""
        patient, created = cls.objects.get_or_create(
            telegram_id=tg_user.id,
            defaults={
                'telegram_first_name': tg_user.first_name or '',
                'telegram_last_name': tg_user.last_name or '',
                'telegram_username': tg_user.username or '',
                'telegram_language': tg_user.language_code or 'uz',
                'first_name': tg_user.first_name or '',
                'last_name': tg_user.last_name or '',
            }
        )
        if not created:
            # Ma'lumotlarni yangilash
            cls.objects.filter(pk=patient.pk).update(
                telegram_first_name=tg_user.first_name or '',
                telegram_username=tg_user.username or '',
            )
        return patient, created


class Patient(TimeStampedModel):
    """
    Klinikaga xos bemor kartasi.
    GlobalPatient + Clinic = munosabati.
    Klinika har bir o'z bemorini alohida boshqaradi.
    """

    global_patient = models.ForeignKey(
        GlobalPatient, on_delete=models.CASCADE,
        related_name='clinic_records', verbose_name='Global bemor',
        null=True, blank=True
    )
    clinic = models.ForeignKey(
        'clinics.Clinic', on_delete=models.CASCADE,
        related_name='patients', verbose_name='Klinika'
    )

    # Klinikaga xos ma'lumotlar
    first_name = models.CharField(max_length=100, verbose_name='Ism')
    last_name = models.CharField(max_length=100, blank=True, verbose_name='Familiya')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan sana")

    GENDER_CHOICES = [('male', '👨 Erkak'), ('female', '👩 Ayol'), ('unknown', '❓ Nomalum')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unknown')

    # Tibbiy ma'lumotlar
    blood_type = models.CharField(
        max_length=5, blank=True, verbose_name='Qon guruhi',
        choices=[('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
                 ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]
    )
    allergies = models.TextField(blank=True, verbose_name='Allergiyalar')
    chronic_diseases = models.TextField(blank=True, verbose_name='Surunkali kasalliklar')
    notes = models.TextField(blank=True, verbose_name='Izohlar')

    # Statistika
    total_visits = models.PositiveIntegerField(default=0)
    last_visit = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Bemor'
        verbose_name_plural = 'Bemorlar'
        ordering = ['-created_at']
        unique_together = [['clinic', 'phone']]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def telegram_id(self):
        if self.global_patient:
            return self.global_patient.telegram_id
        return None

    @property
    def age(self):
        if self.date_of_birth:
            from django.utils import timezone
            return (timezone.now().date() - self.date_of_birth).days // 365
        return None


class MedicalRecord(TimeStampedModel):
    """Bemor tibbiy kartasi yozuvi"""
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE,
        related_name='medical_records', verbose_name='Bemor'
    )
    appointment = models.OneToOneField(
        'appointments.Appointment', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='medical_record'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor', on_delete=models.SET_NULL,
        null=True, related_name='medical_records'
    )
    complaints = models.TextField(verbose_name='Shikoyatlar')
    diagnosis = models.TextField(blank=True, verbose_name='Tashxis')
    treatment = models.TextField(blank=True, verbose_name='Davolash')
    prescription = models.TextField(blank=True, verbose_name='Retsept')
    next_visit = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Tibbiy yozuv'
        verbose_name_plural = 'Tibbiy yozuvlar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.full_name} — {self.created_at.date()}"

    @property
    def debt(self):
        return self.total_amount - self.paid_amount
