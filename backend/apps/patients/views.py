from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db import models
from django_filters import rest_framework as filters
from apps.patients.models import Patient, MedicalRecord, GlobalPatient
from apps.clinics.models import Clinic
from apps.patients.serializers import (
    PatientSerializer, PatientShortSerializer, MedicalRecordSerializer,
    GlobalPatientSerializer
)

class PatientFilter(filters.FilterSet):
    name = filters.CharFilter(method='filter_by_name')

    class Meta:
        model = Patient
        fields = ['gender', 'blood_type']

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            models.Q(first_name__icontains=value) |
            models.Q(last_name__icontains=value)
        )


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = PatientFilter
    search_fields = ['first_name', 'last_name', 'phone', 'telegram_username']
    ordering_fields = ['created_at', 'last_visit', 'total_visits']

    def get_queryset(self):
        user = self.request.user
        clinic_id = self.request.query_params.get('clinic')
        if user.is_staff:
            qs = Patient.objects.all()
        else:
            from apps.clinics.models import Clinic
            clinic_ids = list(
                Clinic.objects.filter(owner=user).values_list('id', flat=True)
            ) + list(
                Clinic.objects.filter(admins=user).values_list('id', flat=True)
            )
            qs = Patient.objects.filter(clinic_id__in=clinic_ids)
        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        return qs

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Bemor tashrif tarixi"""
        patient = self.get_object()
        records = patient.medical_records.all().order_by('-created_at')
        return Response(MedicalRecordSerializer(records, many=True).data)

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """Bemor navbatlari"""
        patient = self.get_object()
        from apps.appointments.serializers import AppointmentListSerializer
        appoints = patient.appointments.all().order_by('-date', '-time')
        return Response(AppointmentListSerializer(appoints, many=True).data)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        patient_id = self.kwargs.get('patient_pk')
        if patient_id:
            return MedicalRecord.objects.filter(patient_id=patient_id)
        return MedicalRecord.objects.none()


class GlobalPatientViewSet(viewsets.ModelViewSet):
    """
    Platform bo'ylab global bemorlar API.
    Asosan Telegram bot orqali murojaat etiladi.
    """
    queryset = GlobalPatient.objects.all()
    serializer_class = GlobalPatientSerializer
    permission_classes = [permissions.AllowAny]  # Hozircha ochiq (bot ishlashi uchun)
    lookup_field = 'telegram_id'

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Telegramdan kelgan yangi bemorni ro'yxatga olish"""
        telegram_id = request.data.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'telegram_id majburiy'}, status=status.HTTP_400_BAD_REQUEST)

        defaults = {
            'telegram_username': request.data.get('telegram_username', ''),
            'telegram_first_name': request.data.get('telegram_first_name', ''),
            'telegram_last_name': request.data.get('telegram_last_name', ''),
            'telegram_language': request.data.get('telegram_language', 'uz'),
            'first_name': request.data.get('telegram_first_name', ''),
            'last_name': request.data.get('telegram_last_name', ''),
        }
        gp, created = GlobalPatient.objects.update_or_create(
            telegram_id=telegram_id, defaults=defaults
        )
        return Response(GlobalPatientSerializer(gp).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def set_language(self, request, telegram_id=None):
        """Klinika bemorni tilini almashtirish"""
        gp = self.get_object()
        lang = request.data.get('language')
        if lang in ['uz', 'ru', 'en']:
            gp.telegram_language = lang
            gp.save(update_fields=['telegram_language'])
            return Response({'ok': True, 'language': lang})
        return Response({'error': 'Noto\'g\'ri til'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def ensure_in_clinic(request):
    """
    Botdan kelgan so'rov: Bemorni ko'rsatilgan klinikaga yozib qo'yish (agar yo'q bo'lsa yaratish)
    """
    telegram_id = request.data.get('telegram_id')
    clinic_id = request.data.get('clinic_id')
    
    if not telegram_id or not clinic_id:
        return Response({'error': 'telegram_id va clinic_id majburiy'}, status=400)
    
    try:
        clinic = Clinic.objects.get(id=clinic_id)
        gp = GlobalPatient.objects.get(telegram_id=telegram_id)
    except (Clinic.DoesNotExist, GlobalPatient.DoesNotExist):
        return Response({'error': 'Klinika yoki Bemor topilmadi'}, status=404)

    # Patient (lokal ulanish) qidiramiz yoki yaratamiz
    patient = Patient.objects.filter(clinic=clinic, global_patient=gp).first()
    if not patient:
        # Balki shu ismda odam bordir (telegram orqali emas)
        phone = gp.phone or f"tg_{gp.telegram_id}"
        patient = Patient.objects.create(
            clinic=clinic,
            global_patient=gp,
            first_name=gp.telegram_first_name or gp.first_name or f"User{gp.telegram_id}",
            last_name=gp.telegram_last_name or gp.last_name or '',
            phone=phone
        )
        # Global statistikani 1 taga oshiramiz
        gp.total_clinics_visited += 1
        gp.save(update_fields=['total_clinics_visited'])

    return Response(PatientSerializer(patient).data)
