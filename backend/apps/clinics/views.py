from rest_framework import status, generics, viewsets, permissions, parsers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from apps.clinics.models import Clinic, ClinicUser, ClinicService, ClinicReview
from apps.clinics.serializers import (
    LoginSerializer, RegisterSerializer, UserSerializer,
    ClinicSerializer, ClinicServiceSerializer, ClinicShortSerializer
)
from apps.clinics.permissions import IsClinicOwnerOrAdmin


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'message': 'Ro\'yxatdan muvaffaqiyatli o\'tdingiz! 30 kunlik bepul sinov boshlandi. 🎉',
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        token = request.data.get('refresh')
        if not token:
            return Response({'error': 'Refresh token kerak'}, status=400)
        try:
            refresh = RefreshToken(token)
            return Response({'access': str(refresh.access_token)})
        except Exception:
            return Response({'error': 'Token noto\'g\'ri yoki muddati o\'tgan'}, status=401)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        data = UserSerializer(user).data
        # Klinikasini ham qo'shamiz
        clinics = Clinic.objects.filter(owner=user) | Clinic.objects.filter(admins=user)
        data['clinics'] = ClinicShortSerializer(clinics.distinct(), many=True).data
        return Response(data)


class ClinicViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicSerializer
    permission_classes = [permissions.IsAuthenticated, IsClinicOwnerOrAdmin]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            qs = Clinic.objects.all()
        else:
            qs = Clinic.objects.filter(owner=user) | Clinic.objects.filter(admins=user)

        # Public filter (bot uchun)
        clinic_type = self.request.query_params.get('clinic_type')
        city = self.request.query_params.get('city')
        is_active = self.request.query_params.get('is_active')
        ordering = self.request.query_params.get('ordering', '-created_at')
        if clinic_type:
            qs = qs.filter(clinic_type=clinic_type)
        if city:
            qs = qs.filter(city__icontains=city)
        if is_active == 'true':
            qs = qs.filter(status__in=['active', 'trial'])
        return qs.order_by(ordering)

    def get_permissions(self):
        # Public read actions
        if self.action in ('by_token', 'review', 'list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsClinicOwnerOrAdmin()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ClinicShortSerializer
        return ClinicSerializer

    @action(detail=False, methods=['get'], url_path='by_token/(?P<token>[^/.]+)')
    def by_token(self, request, token=None):
        """Deep link uchun: /clinics/by_token/abc123ef/"""
        try:
            clinic = Clinic.objects.get(deep_link_token=token)
            return Response(ClinicSerializer(clinic).data)
        except Clinic.DoesNotExist:
            return Response({'error': 'Klinika topilmadi'}, status=404)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Klinikaga reyting va sharh qo'shish"""
        clinic = self.get_object()
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        telegram_id = request.data.get('telegram_id')
        patient_name = request.data.get('patient_name', 'Anonim')
        if not rating or not telegram_id:
            return Response({'error': 'rating va telegram_id kerak'}, status=400)
        ClinicReview.objects.update_or_create(
            clinic=clinic, telegram_id=telegram_id,
            defaults={'rating': rating, 'comment': comment, 'patient_name': patient_name}
        )
        return Response({'ok': True, 'rating': clinic.rating})

    @action(detail=True, methods=['get'])
    def admin_telegram_ids(self, request, pk=None):
        """Klinika adminlarining Telegram ID lari (bot notification uchun)"""
        clinic = self.get_object()
        ids = list(clinic.admins.filter(
            telegram_id__isnull=False
        ).values_list('telegram_id', flat=True))
        if clinic.owner.telegram_id:
            ids.append(clinic.owner.telegram_id)
        return Response({'telegram_ids': list(set(ids))})

    @action(detail=True, methods=['post'])
    def send_broadcast(self, request, pk=None):
        """Klinika bemorlariga bot orqali xabar yuborish (Central yoki Private bot)"""
        clinic = self.get_object()
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Xabar matni kerak'}, status=400)

        from apps.bots.notifications import get_clinic_bot_token, send_telegram_message
        token = get_clinic_bot_token(clinic)
        if not token:
            return Response({'error': 'Bot sozlanmagan'}, status=400)

        # Bemorlarni qidiramiz (telegram_id borlarini)
        from apps.patients.models import Patient
        patients = Patient.objects.filter(
            clinic=clinic, 
            global_patient__telegram_id__isnull=False
        )
        
        sent = 0
        failed = 0
        import time
        for p in patients:
            tid = p.global_patient.telegram_id
            res = send_telegram_message(token, tid, message)
            if res:
                sent += 1
            else:
                failed += 1
            # Flood control uchun kichik pauza
            if sent % 20 == 0:
                time.sleep(1)

        return Response({'sent': sent, 'failed': failed})

    @action(detail=True, methods=['get'])
    def bot_stats(self, request, pk=None):
        clinic = self.get_object()
        appts = clinic.appointments.all()
        bot_patients = clinic.patients.filter(global_patient__telegram_id__isnull=False).count()
        bot_appts = appts.filter(telegram_message_id__isnull=False).count()
        # Simulated/base stats
        visits = clinic.total_appointments * 5 + 10  # Simulation
        
        return Response({
            'bot_users': bot_patients,
            'bot_appts': bot_appts,
            'visits': visits,
            'rating': float(clinic.rating),
            'deep_link_url': clinic.deep_link_url,
            'status': clinic.status
        })

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Klinika dashboard statistikasi"""
        clinic = self.get_object()
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        from apps.appointments.models import Appointment
        appts = Appointment.objects.filter(clinic=clinic)
        
        return Response({
            'clinic': ClinicSerializer(clinic).data,
            'stats': {
                'today_appointments': appts.filter(date=today).count(),
                'week_appointments': appts.filter(date__gte=week_ago).count(),
                'total_patients': clinic.patients.count(),
                'active_doctors': clinic.doctors.filter(is_active=True).count(),
                'pending_appointments': appts.filter(date=today, status='pending').count(),
                'completed_today': appts.filter(date=today, status='completed').count(),
                'rating': float(clinic.rating),
                'review_count': clinic.reviews.count(),
                'deep_link_url': clinic.deep_link_url,
                'public_url': f"https://t.me/ClinckoUzBot?start={clinic.slug}"
            }
        })

    @action(detail=True, methods=['get', 'post'])
    def staff(self, request, pk=None):
        """Klinika xodimlarini boshqarish"""
        clinic = self.get_object()
        from apps.clinics.serializers import UserSerializer
        
        if request.method == 'GET':
            owner_data = UserSerializer(clinic.owner).data
            owner_data['role'] = 'Asoschi'
            
            admins_data = UserSerializer(clinic.admins.all(), many=True).data
            for a in admins_data:
                a['role'] = 'Administrator'
                
            return Response([owner_data] + admins_data)
            
        elif request.method == 'POST':
            # Xodim yaratish (Admin)
            username = request.data.get('username')
            password = request.data.get('password')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            phone = request.data.get('phone', '')

            if not username or not password or not first_name:
                return Response({'error': 'Login, parol va ism kiritilishi shart'}, status=400)
                
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if User.objects.filter(username=username).exists():
                return Response({'error': 'Bunday login band, iltimos boshqasini tanlang'}, status=400)
                
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            
            clinic.admins.add(user)
            res = UserSerializer(user).data
            res['role'] = 'Administrator'
            return Response(res, status=201)

class ClinicServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        clinic_id = self.kwargs.get('clinic_pk')
        return ClinicService.objects.filter(clinic_id=clinic_id)

    def perform_create(self, serializer):
        clinic_id = self.kwargs.get('clinic_pk')
        clinic = Clinic.objects.get(id=clinic_id)
        serializer.save(clinic=clinic)

    @action(detail=False, methods=['get'])
    def health(self, request):
        return Response({'status': 'ok'})
