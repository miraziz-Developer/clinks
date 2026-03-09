from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Count, Sum, Q


class ClinicAnalyticsView(APIView):
    """Klinika analitikasi"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.clinics.models import Clinic
        from apps.appointments.models import Appointment

        clinic_id = request.query_params.get('clinic')
        period = request.query_params.get('period', '30')  # kunlar

        try:
            days = int(period)
        except ValueError:
            days = 30

        # Klinikani topish
        user = request.user
        if user.is_staff:
            clinics = Clinic.objects.all()
        else:
            clinics = Clinic.objects.filter(owner=user) | Clinic.objects.filter(admins=user)

        if clinic_id:
            clinics = clinics.filter(id=clinic_id)

        if not clinics.exists():
            return Response({'error': 'Klinika topilmadi'}, status=404)

        clinic = clinics.first()
        today = timezone.now().date()
        start_date = today - timedelta(days=days)

        appointments = Appointment.objects.filter(
            clinic=clinic,
            date__gte=start_date
        )

        # Kunlik statistika
        daily_stats = []
        for i in range(days):
            d = start_date + timedelta(days=i)
            day_appts = appointments.filter(date=d)
            daily_stats.append({
                'date': str(d),
                'total': day_appts.count(),
                'completed': day_appts.filter(status='completed').count(),
                'cancelled': day_appts.filter(status='cancelled').count(),
                'revenue': float(
                    day_appts.filter(is_paid=True).aggregate(
                        total=Sum('price')
                    )['total'] or 0
                ),
            })

        # Top shifokorlar
        top_doctors = clinic.doctors.annotate(
            appointment_count=Count(
                'appointments',
                filter=Q(appointments__date__gte=start_date)
            )
        ).order_by('-appointment_count')[:5]

        # Umumiy statistika
        total_revenue = appointments.filter(is_paid=True).aggregate(
            total=Sum('price')
        )['total'] or 0

        return Response({
            'clinic': {'id': str(clinic.id), 'name': clinic.name},
            'period': {'days': days, 'start': str(start_date), 'end': str(today)},
            'summary': {
                'total_appointments': appointments.count(),
                'completed': appointments.filter(status='completed').count(),
                'cancelled': appointments.filter(status='cancelled').count(),
                'no_show': appointments.filter(status='no_show').count(),
                'pending': appointments.filter(status='pending').count(),
                'total_revenue': float(total_revenue),
                'total_patients': clinic.patients.count(),
                'new_patients_period': clinic.patients.filter(
                    created_at__date__gte=start_date
                ).count(),
            },
            'daily_stats': daily_stats,
            'top_doctors': [
                {
                    'id': str(d.id),
                    'name': d.full_name,
                    'specialty': d.specialty,
                    'appointments': d.appointment_count,
                }
                for d in top_doctors
            ],
        })


class SuperAdminAnalyticsView(APIView):
    """Super admin — barcha klinikalar statistikasi"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from apps.clinics.models import Clinic, SubscriptionPlan
        from apps.appointments.models import Appointment

        today = timezone.now().date()
        month_ago = today - timedelta(days=30)

        clinics = Clinic.objects.all()

        return Response({
            'total_clinics': clinics.count(),
            'active_clinics': clinics.filter(status='active').count(),
            'trial_clinics': clinics.filter(status='trial').count(),
            'plan_distribution': {
                plan: clinics.filter(plan=plan).count()
                for plan, _ in SubscriptionPlan.choices
            },
            'monthly_revenue': {
                'estimated_usd': (
                    clinics.filter(plan='starter').count() * 20 +
                    clinics.filter(plan='pro').count() * 40 +
                    clinics.filter(plan='enterprise').count() * 80
                ),
            },
            'total_appointments': Appointment.objects.count(),
            'month_appointments': Appointment.objects.filter(date__gte=month_ago).count(),
            'cities': list(
                clinics.values('city').annotate(count=Count('id')).order_by('-count')
            ),
            'recent_clinics': [
                {
                    'name': c.name,
                    'city': c.city,
                    'plan': c.plan,
                    'status': c.status,
                    'created': str(c.created_at.date()),
                }
                for c in clinics.order_by('-created_at')[:10]
            ],
        })
