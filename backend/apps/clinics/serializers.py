from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.clinics.models import ClinicUser, Clinic, ClinicService


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Login yoki parol noto\'g\'ri')
        if not user.is_active:
            raise serializers.ValidationError('Akkaunt faol emas')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = ClinicUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone', 'avatar', 'role']
        read_only_fields = ['id']

    def get_role(self, obj):
        if Clinic.objects.filter(owner=obj).exists():
            return "owner"
        elif Clinic.objects.filter(admins=obj).exists():
            return "admin"
        return "user"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=False)
    clinic_name = serializers.CharField(write_only=True)
    clinic_phone = serializers.CharField(write_only=True, required=False)
    clinic_city = serializers.CharField(write_only=True, required=False, default='Toshkent')
    clinic_address = serializers.CharField(write_only=True, required=False)
    clinic_type = serializers.CharField(write_only=True, required=False, default='general')

    class Meta:
        model = ClinicUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone',
            'password', 'password2',
            'clinic_name', 'clinic_phone', 'clinic_city',
            'clinic_address', 'clinic_type',
        ]

    def validate(self, data):
        # Agar ikkinchi parol berilgan bo'lsa, solishtiramiz
        p2 = data.get('password2')
        if p2 and data['password'] != p2:
            raise serializers.ValidationError({'password2': 'Parollar mos kelmadi'})
        return data

    def create(self, validated_data):
        from django.utils.text import slugify
        import uuid

        # User yaratish
        clinic_data = {
            'clinic_name': validated_data.pop('clinic_name'),
            'clinic_phone': validated_data.pop('clinic_phone', validated_data.get('phone', '')),
            'clinic_city': validated_data.pop('clinic_city', 'Toshkent'),
            'clinic_address': validated_data.pop('clinic_address', 'Manzil kiritilmagan'),
            'clinic_type': validated_data.pop('clinic_type', 'general'),
        }
        validated_data.pop('password2', None)

        user = ClinicUser.objects.create_user(**validated_data)

        # Klinika yaratish
        base_slug = slugify(clinic_data['clinic_name'])
        slug = base_slug
        counter = 1
        while Clinic.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        from django.utils import timezone
        from datetime import timedelta

        clinic = Clinic.objects.create(
            name=clinic_data['clinic_name'],
            slug=slug,
            phone=clinic_data['clinic_phone'],
            city=clinic_data['clinic_city'],
            address=clinic_data['clinic_address'],
            clinic_type=clinic_data['clinic_type'],
            owner=user,
            working_days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
            trial_ends_at=timezone.now() + timedelta(days=30),
        )

        return user


class ClinicServiceSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.IntegerField(source='duration')

    class Meta:
        model = ClinicService
        fields = ['id', 'clinic', 'name', 'description', 'price', 'duration', 'duration_minutes', 'is_active', 'color', 'created_at', 'updated_at']
        read_only_fields = ['id', 'clinic', 'created_at', 'updated_at']



class ClinicSerializer(serializers.ModelSerializer):
    services = ClinicServiceSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    working_days_display = serializers.SerializerMethodField()
    doctor_count = serializers.SerializerMethodField()
    today_appointments = serializers.SerializerMethodField()
    clinic_type_display = serializers.CharField(source='get_clinic_type_display', read_only=True)
    subscription_plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    deep_link_url = serializers.ReadOnlyField()
    public_url = serializers.ReadOnlyField()

    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'slug', 'logo', 'cover_image', 'description', 
            'phone', 'phone2', 'email', 'website', 'address', 'city', 
            'latitude', 'longitude',
            'clinic_type', 'clinic_type_display',
            'plan', 'subscription_plan_display', 'status', 'trial_ends_at', 'subscription_ends_at',
            'work_start', 'work_end', 'lunch_start', 'lunch_end',
            'appointment_duration', 'working_days', 'working_days_display',
            'total_appointments', 'total_patients', 'rating', 'review_count',
            'is_verified', 'is_featured', 'deep_link_token', 'deep_link_url', 'public_url',
            'services', 'owner', 'doctor_count', 'today_appointments',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at', 'updated_at']

    def get_working_days_display(self, obj):
        try:
            return obj.get_working_days_display()
        except:
            return ", ".join(obj.working_days)

    def get_doctor_count(self, obj):
        return obj.doctors.filter(is_active=True).count()

    def get_today_appointments(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        return obj.appointments.filter(date=today).count()


class ClinicShortSerializer(serializers.ModelSerializer):
    """Qisqa ma'lumot - bot uchun"""
    clinic_type_display = serializers.CharField(source='get_clinic_type_display', read_only=True)
    
    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'slug', 'logo', 'cover_image', 
            'phone', 'address', 'city', 'latitude', 'longitude',
            'clinic_type', 'clinic_type_display', 
            'work_start', 'work_end', 'rating', 'review_count'
        ]
