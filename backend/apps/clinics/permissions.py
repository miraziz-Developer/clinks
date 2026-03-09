from rest_framework import permissions


class IsClinicOwnerOrAdmin(permissions.BasePermission):
    """Klinika egasi yoki admini"""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff:
            return True
        # Klinika ob'ekti bo'lsa
        from apps.clinics.models import Clinic
        if isinstance(obj, Clinic):
            return obj.owner == user or user in obj.admins.all()
        # Klinikaga bog'liq ob'ektlar
        if hasattr(obj, 'clinic'):
            return obj.clinic.owner == user or user in obj.clinic.admins.all()
        return False


class IsSuperAdmin(permissions.BasePermission):
    """Faqat super admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsClinicOwner(permissions.BasePermission):
    """Faqat klinika egasi"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'clinic'):
            return obj.clinic.owner == request.user
        return getattr(obj, 'owner', None) == request.user
