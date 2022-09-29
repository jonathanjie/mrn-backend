from rest_framework import permissions


class IsShipUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.assigned_users.all()
