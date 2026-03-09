from rest_framework import serializers
from apps.doctors.models import Doctor, DoctorScheduleException


class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'clinic', 'clinic_name',
            'first_name', 'last_name', 'full_name',
            'phone', 'photo', 'specialty', 'experience_years',
            'bio', 'education', 'achievements',
            'consultation_price', 'services',
            'custom_schedule', 'work_start', 'work_end', 'working_days',
            'is_active', 'total_appointments', 'rating',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'clinic', 'total_appointments', 'rating', 'created_at', 'updated_at']


class DoctorShortSerializer(serializers.ModelSerializer):
    """Qisqa — bot uchun"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'specialty', 'photo', 'consultation_price', 'is_active']


class DoctorAvailableSlotSerializer(serializers.Serializer):
    date = serializers.DateField()
    slots = serializers.ListField(child=serializers.TimeField())
