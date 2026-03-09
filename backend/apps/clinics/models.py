from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from apps.base_models import TimeStampedModel
import uuid


class ClinicUser(AbstractUser):
    """Klinika admin foydalanuvchisi"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return f"{self.get_full_name() or self.username}"


class SubscriptionPlan(models.TextChoices):
    TRIAL = 'trial', '🔓 Sinov (bepul, 30 kun)'
    FREE = 'free', '🆓 Lite (Bepul)'
    STARTER = 'starter', '⭐ Starter ($19/oy)'
    PRO = 'pro', '💎 Pro ($39/oy)'
    BUSINESS = 'business', '🚀 Business ($79/oy)'
    ENTERPRISE = 'enterprise', '🏆 Enterprise (Custom)'


class ClinicStatus(models.TextChoices):
    ACTIVE = 'active', '✅ Faol'
    INACTIVE = 'inactive', '⏸ Nofaol'
    SUSPENDED = 'suspended', '🚫 To\'xtatilgan'
    TRIAL = 'trial', '🔓 Sinov rejimi'


class Clinic(TimeStampedModel):
    """Klinika modeli"""

    # Asosiy ma'lumotlar
    name = models.CharField(max_length=255, verbose_name='Klinika nomi')
    name_uz = models.CharField(max_length=255, blank=True, verbose_name='O\'zbekcha nomi')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    deep_link_token = models.CharField(
        max_length=32, unique=True, blank=True,
        verbose_name='Bot Deep Link Token',
        help_text='t.me/CLinksBot?start=clinic_TOKEN'
    )
    logo = models.ImageField(upload_to='clinic_logos/', null=True, blank=True, verbose_name='Logo')
    cover_image = models.ImageField(upload_to='clinic_covers/', null=True, blank=True, verbose_name='Cover rasm')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    description_uz = models.TextField(blank=True, verbose_name='Tavsif (UZ)')
    description_ru = models.TextField(blank=True, verbose_name='Tavsif (RU)')
    description_en = models.TextField(blank=True, verbose_name='Tavsif (EN)')

    # Aloqa ma'lumotlari
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    phone2 = models.CharField(max_length=20, blank=True, verbose_name='Qo\'shimcha telefon')
    email = models.EmailField(blank=True, verbose_name='Email')
    website = models.URLField(blank=True, verbose_name='Veb-sayt')
    address = models.TextField(verbose_name='Manzil')
    city = models.CharField(max_length=100, verbose_name='Shahar', default='Toshkent')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Klinika turi
    CLINIC_TYPES = [
        ('general', '🏥 Umumiy'),
        ('dental', '🦷 Stomatologiya'),
        ('eye', '👁 Ko\'z klinikasi'),
        ('skin', '🧴 Teri klinikasi'),
        ('neuro', '🧠 Nevrologiya'),
        ('cardio', '❤️ Kardiologiya'),
        ('child', '👶 Bolalar klinikasi'),
        ('other', '🏨 Boshqa'),
    ]
    clinic_type = models.CharField(
        max_length=20, choices=CLINIC_TYPES, default='general',
        verbose_name='Klinika turi'
    )

    # Admin (egasi)
    owner = models.ForeignKey(
        ClinicUser, on_delete=models.PROTECT,
        related_name='owned_clinics', verbose_name='Egasi'
    )
    admins = models.ManyToManyField(
        ClinicUser, related_name='administered_clinics',
        blank=True, verbose_name='Adminlar'
    )

    # Subscription
    plan = models.CharField(
        max_length=20, choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.TRIAL, verbose_name='Tarif'
    )
    status = models.CharField(
        max_length=20, choices=ClinicStatus.choices,
        default=ClinicStatus.TRIAL, verbose_name='Status'
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True, verbose_name='Sinov muddati')
    subscription_ends_at = models.DateTimeField(null=True, blank=True, verbose_name='Obuna muddati')

    # Ish vaqti
    work_start = models.TimeField(default='08:00', verbose_name='Ish boshlanishi')
    work_end = models.TimeField(default='18:00', verbose_name='Ish tugashi')
    lunch_start = models.TimeField(null=True, blank=True, verbose_name='Tushlik boshlanishi')
    lunch_end = models.TimeField(null=True, blank=True, verbose_name='Tushlik tugashi')
    appointment_duration = models.PositiveIntegerField(
        default=30, verbose_name='Navbat davomiyligi (daqiqa)'
    )

    # Dam olish kunlari (JSON: ['monday', 'tuesday', ...])
    working_days = models.JSONField(
        default=list,
        verbose_name='Ish kunlari',
        help_text='["monday","tuesday","wednesday","thursday","friday"]'
    )

    # Statistika
    total_appointments = models.PositiveIntegerField(default=0)
    total_patients = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name='Reyting')
    review_count = models.PositiveIntegerField(default=0, verbose_name='Sharhlar soni')
    is_verified = models.BooleanField(default=False, verbose_name='Tasdiqlangan?')
    is_featured = models.BooleanField(default=False, verbose_name='Featured?')

    class Meta:
        verbose_name = 'Klinika'
        verbose_name_plural = 'Klinikalar'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.deep_link_token:
            import secrets
            self.deep_link_token = secrets.token_hex(8)
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.name) or 'clinic'
            slug = base
            n = 1
            while Clinic.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def deep_link_url(self):
        from django.conf import settings
        bot_username = getattr(settings, 'CENTRAL_BOT_USERNAME', 'Clinko_uzbot')
        return f'https://t.me/{bot_username}?start=clinic_{self.deep_link_token}'

    @property
    def public_url(self):
        return f'https://clinks.uz/clinic/{self.slug}'

    @property
    def is_active(self):
        return self.status in [ClinicStatus.ACTIVE, ClinicStatus.TRIAL]

    @property
    def doctor_limit(self):
        """Tarif bo'ycha shifokor limiti (hozir cheksiz - sinov rejimi)"""
        limits = {
            SubscriptionPlan.TRIAL: 9999,   # Sinov rejimida cheksiz
            SubscriptionPlan.FREE: 1,
            SubscriptionPlan.STARTER: 1,
            SubscriptionPlan.PRO: 10,
            SubscriptionPlan.ENTERPRISE: 9999,
        }
        return limits.get(self.plan, 9999)

    def get_working_days_display(self):
        days_map = {
            'monday': 'Dushanba',
            'tuesday': 'Seshanba',
            'wednesday': 'Chorshanba',
            'thursday': 'Payshanba',
            'friday': 'Juma',
            'saturday': 'Shanba',
            'sunday': 'Yakshanba',
        }
        return [days_map.get(d, d) for d in self.working_days]


class ClinicService(TimeStampedModel):
    """Klinika xizmatlari"""
    clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE,
        related_name='services', verbose_name='Klinika'
    )
    name = models.CharField(max_length=255, verbose_name='Xizmat nomi')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='Narxi (so\'m)'
    )
    duration = models.PositiveIntegerField(
        default=30, verbose_name='Davomiyligi (daqiqa)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Faolmi?')
    color = models.CharField(max_length=7, default='#3B82F6', verbose_name='Rang')

    class Meta:
        verbose_name = 'Xizmat'
        verbose_name_plural = 'Xizmatlar'
        ordering = ['name']

    def __str__(self):
        return f"{self.clinic.name} — {self.name}"


class ClinicInviteToken(TimeStampedModel):
    """Klinika registratsiya uchun taklif token"""
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(ClinicUser, on_delete=models.SET_NULL, null=True)
    used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Taklif tokeni"
        verbose_name_plural = "Taklif tokenlari"


class ClinicReview(TimeStampedModel):
    """Klinika sharhi va reytingi"""
    clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Klinika'
    )
    telegram_id = models.BigIntegerField(verbose_name='Telegram ID')
    patient_name = models.CharField(max_length=100, verbose_name='Bemor ismi')
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f'{i} ⭐') for i in range(1, 6)],
        verbose_name='Reyting'
    )
    comment = models.TextField(blank=True, verbose_name='Sharh')
    is_approved = models.BooleanField(default=True, verbose_name='Tasdiqlangan?')

    class Meta:
        verbose_name = 'Sharh'
        verbose_name_plural = 'Sharhlar'
        ordering = ['-created_at']
        unique_together = [['clinic', 'telegram_id']]

    def __str__(self):
        return f"{self.patient_name} → {self.clinic.name} ({self.rating}⭐)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Klinika reytingini yangilash
        from django.db.models import Avg, Count
        agg = ClinicReview.objects.filter(
            clinic=self.clinic, is_approved=True
        ).aggregate(avg=Avg('rating'), cnt=Count('id'))
        self.clinic.rating = round(agg['avg'] or 0, 2)
        self.clinic.review_count = agg['cnt'] or 0
        self.clinic.save(update_fields=['rating', 'review_count'])
