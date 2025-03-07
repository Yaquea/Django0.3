from rest_framework import permissions

class IsSelf(permissions.BasePermission):
    """
    Custom permission that allows users to view/modify only their own information.

    Usage: Verifies if the requested object belongs to the authenticated user.
    
    Parameters:
        request (HttpRequest): Contains request metadata and authenticated user
        view (APIView): View class handling the request
        obj (Model): Specific model instance being accessed
    """
    def has_object_permission(self, request, view, obj):
        """
        Determines if the authenticated user owns the object
        
        Returns:
            bool: True if user owns the object, False otherwise
        """
        return obj == request.user