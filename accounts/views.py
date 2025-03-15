# views.py
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
# views.py
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token  # Ensure this import is correct

from accounts.serializers import UserSerializer

User = get_user_model()

# Hardcoded admin credentials
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"


class AdminLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Check against hardcoded credentials
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            # Either get existing admin user or create one if it doesn't exist
            admin_user, created = User.objects.get_or_create(
                email=ADMIN_EMAIL,
                defaults={
                    'is_staff': True,
                    'is_superuser': True
                }
            )

            if created:
                admin_user.set_password(ADMIN_PASSWORD)
                admin_user.save()

            # Create token without using Token.objects directly
            try:
                token = Token.objects.get(user=admin_user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=admin_user)

            return Response({
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class HomeView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Welcome to Admin Dashboard'
        }, status=status.HTTP_200_OK)



def admin_login_page(request):
    return render(request, 'admin_login.html')

def admin_dashboard_page(request):
    return render(request, 'home.html')


# ---------------------------------------User CRUD Orignial ADMIN------------------------------------


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def user_management_ui(request):
    # Render the HTML template
    return render(request, 'users_managment.html')