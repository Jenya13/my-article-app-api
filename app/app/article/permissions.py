from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission class for checking if user is owner of the content."""

    def has_object_permission(self, request, view, obj):
        """Check if user is owner of the content."""
        # Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user is the owner of the comment
        is_owner = obj.user == request.user

        return is_owner
