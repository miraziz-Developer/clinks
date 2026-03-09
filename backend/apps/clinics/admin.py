from django.contrib import admin
from django.utils.html import format_html
from apps.clinics.models import Clinic, ClinicUser, ClinicService, ClinicInviteToken


@admin.register(ClinicUser)
class ClinicUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_full_name', 'email', 'phone', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['date_joined', 'last_login']


class ClinicServiceInline(admin.TabularInline):
    model = ClinicService
    extra = 1
    fields = ['name', 'price', 'duration', 'is_active', 'color']


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'city', 'clinic_type', 'plan_badge', 'status_badge',
        'doctor_count', 'total_appointments', 'created_at'
    ]
    list_filter = ['status', 'plan', 'clinic_type', 'city']
    search_fields = ['name', 'phone', 'owner__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_appointments', 'total_patients']
    inlines = [ClinicServiceInline]
    fieldsets = (
        ('Asosiy', {
            'fields': ('name', 'slug', 'logo', 'description', 'clinic_type', 'owner')
        }),
        ('Aloqa', {
            'fields': ('phone', 'phone2', 'email', 'address', 'city', 'website')
        }),
        ('Obuna', {
            'fields': ('plan', 'status', 'trial_ends_at', 'subscription_ends_at')
        }),
        ('Ish vaqti', {
            'fields': ('work_start', 'work_end', 'lunch_start', 'lunch_end',
                       'appointment_duration', 'working_days')
        }),
        ('Statistika', {
            'fields': ('total_appointments', 'total_patients'),
            'classes': ('collapse',)
        }),
    )

    def plan_badge(self, obj):
        colors = {
            'trial': '#6B7280',
            'starter': '#10B981',
            'pro': '#3B82F6',
            'enterprise': '#8B5CF6',
            'free': '#9CA3AF',
        }
        color = colors.get(obj.plan, '#gray')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            color, obj.get_plan_display()
        )
    plan_badge.short_description = 'Tarif'

    def status_badge(self, obj):
        colors = {
            'active': '#10B981',
            'inactive': '#9CA3AF',
            'suspended': '#EF4444',
            'trial': '#F59E0B',
        }
        color = colors.get(obj.status, '#gray')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def doctor_count(self, obj):
        count = obj.doctors.filter(is_active=True).count()
        return format_html('<b>{}</b> ta', count)
    doctor_count.short_description = 'Shifokorlar'


@admin.register(ClinicService)
class ClinicServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'clinic', 'price', 'duration', 'is_active']
    list_filter = ['is_active', 'clinic']
    search_fields = ['name', 'clinic__name']
