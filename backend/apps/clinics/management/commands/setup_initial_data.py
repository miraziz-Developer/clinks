"""
Superuser yaratish va demo data qo'shish
Usage: python manage.py setup_initial_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Boshlang\'ich ma\'lumotlarni yaratish'

    def add_arguments(self, parser):
        parser.add_argument('--with-demo', action='store_true', help='Demo ma\'lumotlar qo\'shish')

    def handle(self, *args, **options):
        from apps.clinics.models import ClinicUser, Clinic, ClinicService

        # Super admin yaratish
        if not ClinicUser.objects.filter(username='admin').exists():
            admin = ClinicUser.objects.create_superuser(
                username='admin',
                email='admin@clinks.uz',
                password='admin123',
                first_name='Super',
                last_name='Admin',
            )
            self.stdout.write(self.style.SUCCESS('✅ Super admin yaratildi: admin / admin123'))
        else:
            admin = ClinicUser.objects.get(username='admin')
            self.stdout.write('ℹ️  Super admin allaqachon mavjud')

        if options['with_demo']:
            self._create_demo_data(admin)

    def _create_demo_data(self, admin):
        from apps.clinics.models import ClinicUser, Clinic, ClinicService
        from apps.doctors.models import Doctor
        from apps.patients.models import Patient, MedicalRecord
        from apps.appointments.models import Appointment

        # Demo klinika foydalanuvchisi
        user, _ = ClinicUser.objects.get_or_create(
            username='demo_clinic',
            defaults={
                'email': 'demo@clinic.uz',
                'first_name': 'Demo',
                'last_name': 'Egasi',
                'phone': '+998901234567',
            }
        )
        user.set_password('demo123')
        user.save()

        # Demo klinika
        clinic, created = Clinic.objects.get_or_create(
            slug='demo-stomatologiya',
            defaults={
                'name': 'Demo Stomatologiya',
                'phone': '+998712345678',
                'address': 'Toshkent sh., Chilonzor tumani, 3-mavze',
                'city': 'Toshkent',
                'clinic_type': 'dental',
                'owner': user,
                'working_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
                'work_start': '09:00',
                'work_end': '18:00',
                'trial_ends_at': timezone.now() + timedelta(days=30),
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Demo klinika yaratildi: {clinic.name}'))

            # Xizmatlar
            services_data = [
                ('Stomatologik ko\'rik', 50000, 30),
                ('Tish plombasi', 200000, 60),
                ('Tish oqartirish', 500000, 90),
                ('Implant', 2000000, 120),
            ]
            services = []
            for name, price, duration in services_data:
                s = ClinicService.objects.create(
                    clinic=clinic, name=name, price=price, duration=duration
                )
                services.append(s)

            # Shifokorlar
            doctors_data = [
                ('Karimov', 'Jamshid', 'Stomatolog', 8, 150000),
                ('Toshmatova', 'Malika', 'Ortodont', 5, 200000),
                ('Yusupov', 'Bobur', 'Xirurg-stomatolog', 12, 250000),
            ]
            for last, first, spec, exp, price in doctors_data:
                doc = Doctor.objects.create(
                    clinic=clinic,
                    first_name=first,
                    last_name=last,
                    specialty=spec,
                    experience_years=exp,
                    consultation_price=price,
                    phone='+998901234567',
                )
                doc.services.set(services[:2])

            # Demo bemorlar
            patients_data = [
                ('Ahmedov', 'Jasur', '+998901111111'),
                ('Karimova', 'Nodira', '+998902222222'),
                ('Toshev', 'Sherzod', '+998903333333'),
            ]
            for last, first, phone in patients_data:
                Patient.objects.create(
                    clinic=clinic,
                    first_name=first,
                    last_name=last,
                    phone=phone,
                )

            self.stdout.write(self.style.SUCCESS('✅ Demo ma\'lumotlar yaratildi!'))
            self.stdout.write('---')
            self.stdout.write(f'Klinika admin: demo_clinic / demo123')
            self.stdout.write(f'Super admin: admin / admin123')
            self.stdout.write(f'Admin panel: http://localhost/admin/')
            self.stdout.write(f'API docs: http://localhost/api/docs/')
