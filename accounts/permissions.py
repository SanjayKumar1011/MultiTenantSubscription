from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == 'OWNER'
        )
    
class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ['ADMIN', 'OWNER']
        )
    
class IsMember(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == 'MEMBER'
        )
    
