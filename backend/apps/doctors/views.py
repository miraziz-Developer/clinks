from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import date, timedelta
from apps.doctors.models import Doctor
from apps.doctors.serializers import (
    DoctorSerializer, DoctorShortSerializer, DoctorAvailableSlotSerializer
)
from apps.clinics.permissions import IsClinicOwnerOrAdmin


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        clinic_id = self.request.query_params.get('clinic')
        is_active = self.request.query_params.get('is_active')
        
        if getattr(user, 'is_authenticated', False):
            if user.is_staff:
                qs = Doctor.objects.all()
            else:
                from apps.clinics.models import Clinic
                clinic_ids = list(
                    Clinic.objects.filter(owner=user).values_list('id', flat=True)
                ) + list(
                    Clinic.objects.filter(admins=user).values_list('id', flat=True)
                )
                qs = Doctor.objects.filter(clinic_id__in=clinic_ids)
        else:
            # Public/Bot access - must provide clinic_id
            if not clinic_id:
                return Doctor.objects.none()
            qs = Doctor.objects.filter(clinic_id=clinic_id)

        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        if is_active == 'true':
            qs = qs.filter(is_active=True)
            
        return qs.select_related('clinic')

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'available_slots', 'week_schedule'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        clinic_id = self.request.data.get('clinic')
        from apps.clinics.models import Clinic
        clinic = Clinic.objects.get(id=clinic_id)
        doctor = serializer.save(clinic=clinic)
        
        # User requested to create login for this doctor
        if self.request.data.get('create_login') == 'true' or self.request.data.get('create_login') is True:
            from django.contrib.auth import get_user_model
            from django.utils.crypto import get_random_string
            from django.utils.text import slugify
            User = get_user_model()
            
            base_username = slugify(f"{doctor.first_name} {doctor.last_name}").replace('-', '')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            password = get_random_string(8)
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=doctor.first_name,
                last_name=doctor.last_name,
                phone=doctor.phone
            )
            # Add doctor user to admins so they can login to staff portal
            clinic.admins.add(user)
            
            # Save generated credentials temporarily on doctor object to return in response
            doctor._generated_username = username
            doctor._generated_password = password
            
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        doctor = serializer.instance
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        
        if hasattr(doctor, '_generated_username'):
            data['generated_username'] = doctor._generated_username
            data['generated_password'] = doctor._generated_password
            
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def available_slots(self, request, pk=None):
        """Shifokorning bo'sh vaqtlari"""
        doctor = self.get_object()
        date_str = request.query_params.get('date', str(timezone.now().date()))
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return Response({'error': 'Sana formati noto\'g\'ri. YYYY-MM-DD formatida yuboring'}, status=400)

        slots = doctor.get_available_slots(target_date)
        # Convert time objects to strings
        slots_str = [t.strftime('%H:%M') for t in slots]
        
        return Response({
            'doctor': DoctorShortSerializer(doctor).data,
            'date': date_str,
            'slots': slots_str,
            'total_slots': len(slots_str),
        })

    @action(detail=True, methods=['get'])
    def week_schedule(self, request, pk=None):
        """Haftalik jadval"""
        doctor = self.get_object()
        today = timezone.now().date()
        week_data = []

        for i in range(7):
            d = today + timedelta(days=i)
            slots = doctor.get_available_slots(d)
            week_data.append({
                'date': str(d),
                'day_name': d.strftime('%A'),
                'available_slots': len(slots),
                'slots': slots[:5],  # Faqat birinchi 5 ta
            })

        return Response(week_data)
