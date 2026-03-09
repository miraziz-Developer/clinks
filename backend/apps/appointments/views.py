from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.utils import timezone
from apps.appointments.models import Appointment, AppointmentStatus
from apps.appointments.serializers import (
    AppointmentCreateSerializer, AppointmentListSerializer,
    AppointmentDetailSerializer, AppointmentStatusUpdateSerializer
)


class AppointmentFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    doctor = filters.UUIDFilter(field_name='doctor_id')
    status = filters.ChoiceFilter(choices=AppointmentStatus.choices)

    class Meta:
        model = Appointment
        fields = ['status', 'is_paid', 'date', 'clinic']


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AppointmentFilter
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__phone']
    ordering_fields = ['date', 'time', 'created_at']

    def get_queryset(self):
        user = self.request.user
        clinic_id = self.request.query_params.get('clinic')
        tid = self.request.query_params.get('telegram_id')
        
        if user.is_authenticated:
            if user.is_staff:
                qs = Appointment.objects.all()
            else:
                from apps.clinics.models import Clinic
                clinic_ids = list(
                    Clinic.objects.filter(owner=user).values_list('id', flat=True)
                ) + list(
                    Clinic.objects.filter(admins=user).values_list('id', flat=True)
                )
                qs = Appointment.objects.filter(clinic_id__in=clinic_ids)
        elif tid:
            # Public/Bot access - filter by GlobalPatient's telegram_id
            qs = Appointment.objects.filter(patient__global_patient__telegram_id=tid)
        else:
            return Appointment.objects.none()

        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        return qs.select_related('patient', 'doctor', 'clinic', 'service')

    def get_permissions(self):
        if self.action in ('list', 'create', 'retrieve', 'update_status'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        elif self.action in ['retrieve']:
            return AppointmentDetailSerializer
        return AppointmentListSerializer

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason', '')

        if new_status == AppointmentStatus.CONFIRMED:
            appointment.confirm()
        elif new_status == AppointmentStatus.CANCELLED:
            appointment.cancel(reason=reason, cancelled_by='clinic')
        elif new_status == AppointmentStatus.COMPLETED:
            appointment.complete()
        else:
            appointment.status = new_status
            appointment.save()

        return Response(AppointmentListSerializer(appointment).data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        appointment = self.get_object()
        appointment.is_paid = True
        appointment.save()
        return Response({'status': 'to\'langan', 'is_paid': True})

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Bugungi navbatlar"""
        clinic_id = request.query_params.get('clinic')
        qs = self.get_queryset().filter(date=timezone.now().date())
        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)
        qs = qs.order_by('time')
        return Response(AppointmentListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Kelgusi navbatlar"""
        qs = self.get_queryset().filter(
            date__gte=timezone.now().date(),
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).order_by('date', 'time')[:50]
        return Response(AppointmentListSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Navbat statistikasi"""
        from django.db.models import Sum, Count
        from datetime import timedelta
        clinic_id = request.query_params.get('clinic')
        qs = self.get_queryset()
        if clinic_id:
            qs = qs.filter(clinic_id=clinic_id)

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        # Basic Stats
        total = qs.count()
        unique_patients = qs.values('patient').distinct().count()
        doctors_count = qs.values('doctor').distinct().count()
        total_revenue = qs.filter(is_paid=True).aggregate(total=Sum('price'))['total'] or 0

        # Status counts
        status_counts = qs.values('status').annotate(count=Count('id'))
        status_dict = {s[0]: 0 for s in AppointmentStatus.choices}
        for s in status_counts:
            status_dict[s['status']] = s['count']

        # Today's breakdown
        today_qs = qs.filter(date=today)

        return Response({
            'total': total,
            'unique_patients': unique_patients,
            'doctors_count': doctors_count,
            'total_revenue': float(total_revenue),
            'status_breakdown': status_dict,
            'today': {
                'total': today_qs.count(),
                'confirmed': today_qs.filter(status=AppointmentStatus.CONFIRMED).count(),
                'completed': today_qs.filter(status=AppointmentStatus.COMPLETED).count(),
                'cancelled': today_qs.filter(status=AppointmentStatus.CANCELLED).count(),
            }
        })
