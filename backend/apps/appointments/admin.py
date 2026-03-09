from django.contrib import admin
from django.utils.html import format_html
from apps.appointments.models import Appointment, AppointmentStatus


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'patient_name', 'doctor_name', 'date', 'time',
        'status_badge', 'paid_badge', 'price', 'clinic'
    ]
    list_filter = ['status', 'is_paid', 'date', 'clinic', 'doctor']
    search_fields = [
        'patient__first_name', 'patient__last_name',
        'patient__phone', 'doctor__last_name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'telegram_message_id']
    date_hierarchy = 'date'
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    fieldsets = (
        ('Asosiy', {
            'fields': ('clinic', 'doctor', 'patient', 'service')
        }),
        ('Vaqt', {
            'fields': ('date', 'time', 'duration')
        }),
        ('Status', {
            'fields': ('status', 'complaint', 'notes', 'cancellation_reason', 'cancelled_by')
        }),
        ('To\'lov', {
            'fields': ('price', 'is_paid')
        }),
        ('Telegram', {
            'fields': ('telegram_message_id', 'reminder_sent', 'reminder_24h_sent'),
            'classes': ('collapse',)
        }),
    )

    def patient_name(self, obj):
        return obj.patient.full_name
    patient_name.short_description = 'Bemor'

    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.last_name}"
    doctor_name.short_description = 'Shifokor'

    def status_badge(self, obj):
        colors = {
            'pending': '#F59E0B',
            'confirmed': '#3B82F6',
            'completed': '#10B981',
            'cancelled': '#EF4444',
            'no_show': '#6B7280',
            'rescheduled': '#8B5CF6',
        }
        color = colors.get(obj.status, '#gray')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:10px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def paid_badge(self, obj):
        if obj.is_paid:
            return format_html(
                '<span style="background:#10B981;color:white;padding:2px 8px;'
                'border-radius:10px;font-size:11px">✅ To\'langan</span>'
            )
        return format_html(
            '<span style="background:#EF4444;color:white;padding:2px 8px;'
            'border-radius:10px;font-size:11px">❌ Kutilmoqda</span>'
        )
    paid_badge.short_description = 'To\'lov'

    @admin.action(description='✅ Tasdiqlash')
    def mark_confirmed(self, request, queryset):
        for obj in queryset:
            obj.confirm()
        self.message_user(request, f'{queryset.count()} ta navbat tasdiqlandi')

    @admin.action(description='✔️ Tugallangan deb belgilash')
    def mark_completed(self, request, queryset):
        for obj in queryset:
            obj.complete()
        self.message_user(request, f'{queryset.count()} ta navbat tugallandi')

    @admin.action(description='❌ Bekor qilish')
    def mark_cancelled(self, request, queryset):
        queryset.update(status=AppointmentStatus.CANCELLED)
        self.message_user(request, f'{queryset.count()} ta navbat bekor qilindi')
