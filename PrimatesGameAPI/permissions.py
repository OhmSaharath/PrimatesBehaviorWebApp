
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Custom permission to only allow superusers
    """
    def has_permission(self, request, view):
        # Check if the user belongs to the superuser
        return request.user.is_superuser

class IsResearcher(BasePermission):
    """
    Custom permission to only allow managers to access.
    """

    def has_permission(self, request, view):
        # Check if the user belongs to the "Researcher" group 
        return request.user.groups.filter(name='Researcher').exists()
    
class IsResearcherOrAdmin(BasePermission):
    """
    Custom permission to only allow managers and superusers to access.
    """
    def has_permission(self, request, view):
        # Check if the user belongs to the "Researcher" group or admin
        return request.user.groups.filter(name='Researcher').exists() or request.user.is_superuser
    
    
class IsRPiClient(BasePermission):
    """
    Custom permission to only allow RPiClient to access.
    """
    def has_permission(self, request, view):
        # Check if the user belongs to the "RPiClient" group 
        return request.user.groups.filter(name='RPiClient').exists() 
