from rest_framework import serializers
from apps.appointments.models import Appointment, AppointmentStatus
from apps.patients.serializers import PatientShortSerializer
from apps.doctors.serializers import DoctorShortSerializer


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'clinic', 'doctor', 'patient', 'service',
            'date', 'time', 'complaint', 'notes', 'price',
        ]

    def validate(self, data):
        doctor = data.get('doctor')
        date = data.get('date')
        time = data.get('time')

        # Shifokor ushbu vaqtda band emasligini tekshirish
        if Appointment.objects.filter(
            doctor=doctor, date=date, time=time,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).exists():
            raise serializers.ValidationError(
                {'time': f'Shifokor {date} kuni {time} da band. Boshqa vaqt tanlang.'}
            )

        # O'tgan sanaga navbat olishni oldini olish
        from django.utils import timezone
        if date < timezone.now().date():
            raise serializers.ValidationError({'date': 'O\'tgan sanaga navbat olish mumkin emas'})

        return data

    def create(self, validated_data):
        clinic = validated_data.get('clinic')
        validated_data['duration'] = clinic.appointment_duration
        appointment = super().create(validated_data)
        # Tasdiqlash xabarini yuborish
        appointment._send_confirmation_notification()
        return appointment


class AppointmentListSerializer(serializers.ModelSerializer):
    patient = PatientShortSerializer(read_only=True)
    doctor = DoctorShortSerializer(read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    end_time = serializers.ReadOnlyField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'clinic', 'clinic_name', 'doctor', 'doctor_name',
            'patient', 'service',
            'date', 'time', 'end_time', 'duration',
            'status', 'status_display',
            'complaint', 'notes', 'price', 'is_paid',
            'reminder_sent', 'created_at',
        ]


class AppointmentDetailSerializer(AppointmentListSerializer):
    class Meta(AppointmentListSerializer.Meta):
        fields = AppointmentListSerializer.Meta.fields + [
            'telegram_message_id', 'cancellation_reason',
            'cancelled_by', 'updated_at',
        ]


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=AppointmentStatus.choices)
    reason = serializers.CharField(required=False, allow_blank=True)
