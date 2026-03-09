from django.contrib import admin
from django.utils.html import format_html
from apps.doctors.models import Doctor, DoctorScheduleException


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        'photo_preview', 'full_name', 'specialty', 'clinic',
        'experience_years', 'consultation_price', 'is_active', 'total_appointments'
    ]
    list_filter = ['is_active', 'clinic', 'specialty']
    search_fields = ['first_name', 'last_name', 'phone', 'clinic__name']
    readonly_fields = ['id', 'total_appointments', 'rating', 'created_at', 'photo_preview']
    filter_horizontal = ['services']

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover">',
                obj.photo.url
            )
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;background:#3B82F6;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold">'
            '{}</div>', obj.first_name[0] if obj.first_name else '?'
        )
    photo_preview.short_description = 'Foto'


@admin.register(DoctorScheduleException)
class DoctorScheduleExceptionAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'is_working', 'reason']
    list_filter = ['is_working', 'date']
