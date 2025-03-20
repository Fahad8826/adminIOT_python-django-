# views.py
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Farm
from .serializers import FarmSerializer


class IsAdminOrManagerOrOwner(permissions.BasePermission):
    """
    Custom permission for role-based access:
    - Admins can access all farms
    - Managers can access all farms
    - Regular users can only access their own farms
    """

    def has_object_permission(self, request, view, obj):
        # Allow admins and managers full access
        if request.user.role in ['admin', 'manager']:
            return True
        # Regular users can only access their own farms
        return obj.owner == request.user




class FarmListCreateView(generics.ListCreateAPIView):
    """
    List all farms or create a new farm.
    Admins and managers can specify the owner, while regular users are automatically assigned as the owner.
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerOrOwner]

    def get_queryset(self):
        """
        Return all farms for admins/managers, or only user's farms for regular users.
        """
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Farm.objects.all()
        return Farm.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        Allow admins/managers to specify owner, otherwise set to current user.
        """
        user = self.request.user

        if user.role in ['admin', 'manager']:
            # Admins and managers can specify the owner
            owner_id = self.request.data.get('owner')
            if owner_id:
                # Save the farm with the specified owner
                serializer.save(owner_id=owner_id)
            else:
                # If no owner is specified, default to the current user
                serializer.save(owner=user)
        else:
            # Regular users can only create farms for themselves
            serializer.save(owner=user)


class FarmDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a farm instance
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManagerOrOwner]

    def get_queryset(self):
        """
        Return all farms for admins/managers, or only user's farms for regular users
        """
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Farm.objects.all()
        return Farm.objects.filter(owner=user)


from django.shortcuts import render

def create_farm_page(request):
    return render(request, 'create_farm.html')