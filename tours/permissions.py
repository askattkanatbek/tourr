from rest_framework import permissions

class IsTourCreator(permissions.BasePermission):
    """
        Доступ разрешён только пользователям с ролью 'creator'
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'creator'