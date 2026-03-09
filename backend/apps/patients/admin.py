from django.contrib import admin
from apps.patients.models import Patient, MedicalRecord


class MedicalRecordInline(admin.StackedInline):
    model = MedicalRecord
    extra = 0
    readonly_fields = ['created_at']
    fields = ['doctor', 'complaints', 'diagnosis', 'treatment', 'prescription',
              'total_amount', 'paid_amount', 'next_visit', 'notes', 'created_at']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'phone', 'clinic', 'gender', 'age',
        'total_visits', 'last_visit', 'created_at'
    ]
    list_filter = ['gender', 'clinic', 'blood_type']
    search_fields = ['first_name', 'last_name', 'phone', 'telegram_username']
    readonly_fields = ['id', 'total_visits', 'last_visit', 'created_at', 'updated_at']
    inlines = [MedicalRecordInline]

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Ism Familiya'

    def age(self, obj):
        return obj.age
    age.short_description = 'Yosh'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'diagnosis', 'total_amount', 'paid_amount', 'created_at']
    list_filter = ['doctor__clinic']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis']
    readonly_fields = ['id', 'created_at', 'updated_at']
