from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    #Разрешает доступ только admin

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) =='admin'
        )