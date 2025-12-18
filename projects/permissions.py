from rest_framework.permissions import BasePermission, SAFE_METHODS


class ProjectPermission(BasePermission):
    """
    OWNER  → full access
    ADMIN  → read & update
    MEMBER → read only
    """

    def has_object_permission(self, request, view, obj):

        # Read-only allowed for all roles
        if request.method in SAFE_METHODS:
            return True

        # OWNER can do anything
        if request.user.role == 'OWNER':
            return True

        # ADMIN can update but not delete
        if request.user.role == 'ADMIN':
            return request.method in ['PUT', 'PATCH']

        # MEMBER cannot modify
        return False