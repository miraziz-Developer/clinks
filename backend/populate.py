import os
import django
from datetime import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic, ClinicUser, ClinicService, ClinicStatus
from apps.doctors.models import Doctor

user, _ = ClinicUser.objects.get_or_create(
    username='demo_admin', 
    defaults={
        'first_name': 'SuperAdmin',
        'is_staff': True,
        'is_superuser': True
    }
)
user.set_password('clinks123')
user.save()

clinic, created = Clinic.objects.get_or_create(
    slug='toshkent-premium-med',
    defaults={
        'owner': user,
        'name': 'Toshkent Premium Med',
        'city': 'Toshkent',
        'address': 'Amir Temur shoh ko\'chasi, 15',
        'phone': '+998901234567',
        'clinic_type': 'general',
        'status': ClinicStatus.ACTIVE,
        'rating': 4.90,
        'review_count': 120,
        'description': 'Toshkentdagi eng raqamli va zamonaviy ko\'p tarmoqli tibbiyot markazi.',
        'is_featured': True,
        'is_verified': True,
        'work_start': '08:00',
        'work_end': '20:00',
        'appointment_duration': 30,
        'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    }
)

if created:
    Doctor.objects.create(
        clinic=clinic,
        first_name='Alisher',
        last_name='Usmonov',
        specialty='Kardiolog',
        experience_years=15,
        consultation_price=150000,
        is_active=True,
        phone='+998901112233'
    )
    ClinicService.objects.create(
        clinic=clinic,
        name='Kardiologik ko\'rik (EKG bilan)',
        price=150000,
        duration=30
    )

print(f"Bazada jami: {Clinic.objects.count()} klinika va {Doctor.objects.count()} shifokor bor!")
