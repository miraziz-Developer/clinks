from rest_framework import serializers
from apps.patients.models import Patient, MedicalRecord, GlobalPatient


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = [
            'id', 'clinic', 'global_patient',
            'first_name', 'last_name', 'full_name', 'phone',
            'date_of_birth', 'age', 'gender',

            'blood_type', 'allergies', 'chronic_diseases', 'notes',
            'total_visits', 'last_visit', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'clinic', 'total_visits', 'last_visit', 'created_at', 'updated_at']


class PatientShortSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'phone', 'total_visits', 'last_visit']


class GlobalPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalPatient
        fields = '__all__'


class MedicalRecordSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    debt = serializers.ReadOnlyField()

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'appointment', 'doctor', 'doctor_name',
            'complaints', 'diagnosis', 'treatment', 'prescription',
            'next_visit', 'notes',
            'total_amount', 'paid_amount', 'debt',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
