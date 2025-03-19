# views.py
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import ListView, DetailView, CreateView, UpdateView
# views.py
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token  # Ensure this import is correct

from AdminIOT import settings
from accounts.serializers import UserSerializer

User = get_user_model()  # This will get your custom User or the default User

# Constants for admin credentials



ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"


class AdminLoginView(APIView):
    permission_classes = [AllowAny]  # Important! Allow anyone to access this endpoint

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Log the login attempt (only in development)
        print(f"Login attempt for email: {email}")

        # Check if email or password is missing
        if not email or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # First check if a user with this email exists
        try:
            user = User.objects.get(email=email)
            print(f"User found: {user.email}, is_superuser: {user.is_superuser}")

            # Check if user has admin role
            has_admin_role = False
            if hasattr(user, 'role'):
                has_admin_role = user.role == 'admin'
                print(f"User role check: {user.role}, has admin role: {has_admin_role}")

            # Check if user is superuser or has admin role
            is_admin = user.is_superuser or has_admin_role

            # Verify password
            password_valid = user.check_password(password)
            print(f"Password check: {password_valid}")

            if is_admin and password_valid:
                # Create or get token
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'message': 'Login successful',
                    'user_id': user.id,
                    'email': user.email,
                    'is_admin': True
                }, status=status.HTTP_200_OK)
            elif not is_admin:
                return Response({
                    'error': 'This user does not have admin privileges'
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'error': 'Invalid password'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            print(f"User not found with email: {email}")
            # User doesn't exist, check against hardcoded admin credentials
            pass

        # Check against hardcoded credentials as fallback
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            print("Using hardcoded admin credentials")
            # Either get existing admin user or create one if it doesn't exist
            try:
                admin_user = User.objects.get(email=ADMIN_EMAIL)
                print(f"Found hardcoded admin user: {admin_user.email}")
            except User.DoesNotExist:
                print("Creating new hardcoded admin user")
                # If using default User model
                if hasattr(User, 'username'):
                    admin_user = User.objects.create(
                        username='admin',  # Username is required in default User model
                        email=ADMIN_EMAIL,
                        is_staff=True,
                        is_superuser=True,
                    )
                    if hasattr(admin_user, 'role'):
                        admin_user.role = 'admin'
                    admin_user.set_password(ADMIN_PASSWORD)
                    admin_user.save()
                else:
                    # If using custom User model where email is the username field
                    admin_user = User.objects.create(
                        email=ADMIN_EMAIL,
                        is_staff=True,
                        is_superuser=True,
                    )
                    if hasattr(admin_user, 'role'):
                        admin_user.role = 'admin'
                    admin_user.set_password(ADMIN_PASSWORD)
                    admin_user.save()

            # Create or get token
            token, created = Token.objects.get_or_create(user=admin_user)

            return Response({
                'token': token.key,
                'message': 'Login successful',
                'user_id': admin_user.id,
                'email': admin_user.email,
                'is_admin': True
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


class HomeView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can access this view

    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Welcome to Admin Dashboard'
        }, status=status.HTTP_200_OK)

# Template views
@ensure_csrf_cookie  # This adds CSRF token to the response
def admin_login_page(request):
    return render(request, 'admin_login.html')


from django.contrib.auth.decorators import user_passes_test, login_required


def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard_page(request):
    return render(request, 'home.html')


# Admin signup view for API
class AdminSignupView(APIView):
    permission_classes = [IsAdminUser]  # Only existing admins can create new admins

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('username')

        if not email or not password:
            return Response({
                'error': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create new admin user
        try:
            # Handle both username-based and email-based User models
            if hasattr(User, 'username') and User._meta.get_field('username').unique:
                if not username:
                    # Generate username from email if not provided
                    username = email.split('@')[0]
                    # Make sure username is unique
                    base_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                admin_user = User.objects.create(
                    username=username,
                    email=email,
                    is_staff=True,
                    is_superuser=True
                )
            else:
                # Email-based User model
                admin_user = User.objects.create(
                    email=email,
                    is_staff=True,
                    is_superuser=True
                )

            # Set role if available
            if hasattr(admin_user, 'role'):
                admin_user.role = 'admin'

            admin_user.set_password(password)
            admin_user.save()

            # Create token for the new admin
            token, created = Token.objects.get_or_create(user=admin_user)

            return Response({
                'message': 'Admin user created successfully',
                'email': email,
                'token': token.key
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Super Admin signup view (first admin creation with master password)
class SuperAdminSignupView(APIView):
    permission_classes = [AllowAny]  # Anyone can access this endpoint

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        master_password = request.data.get('master_password')
        username = request.data.get('username')

        # Check master password (should be stored securely in settings or environment)
        MASTER_PASSWORD = getattr(settings, 'MASTER_ADMIN_PASSWORD', 'master_secret_password')

        if master_password != MASTER_PASSWORD:
            return Response({
                'error': 'Invalid master password'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if any admin already exists
        if User.objects.filter(is_superuser=True).exists():
            return Response({
                'error': 'Super admin already exists. Use regular admin signup.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create first super admin
        try:
            # Handle both username-based and email-based User models
            if hasattr(User, 'username') and User._meta.get_field('username').unique:
                if not username:
                    username = email.split('@')[0]

                admin_user = User.objects.create(
                    username=username,
                    email=email,
                    is_staff=True,
                    is_superuser=True
                )
            else:
                admin_user = User.objects.create(
                    email=email,
                    is_staff=True,
                    is_superuser=True
                )

            if hasattr(admin_user, 'role'):
                admin_user.role = 'admin'

            admin_user.set_password(password)
            admin_user.save()

            token, created = Token.objects.get_or_create(user=admin_user)

            return Response({
                'message': 'Super admin created successfully',
                'email': email,
                'token': token.key
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Template view for admin signup page
@ensure_csrf_cookie
def admin_signup_page(request):
    # Check if user is already authenticated as admin
    is_admin = request.user.is_authenticated and request.user.is_staff
    # Check if any admin exists
    admin_exists = User.objects.filter(is_superuser=True).exists()

    context = {
        'is_admin': is_admin,
        'admin_exists': admin_exists
    }

    return render(request, 'admin_signup.html', context)
# ---------------------------------------User CRUD Orignial ADMIN------------------------------------


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer



# -------------------------------userlogin----------------------------------------

class UserLoginView(APIView):
    permission_classes = [AllowAny]  # Allow login without authentication

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------userlogout-------------------------------------


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can log out

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()  # Remove the token from the database
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Invalid request or already logged out"}, status=status.HTTP_400_BAD_REQUEST)



def user_management_ui(request):
    # Render the HTML template
    return render(request, 'users_managment.html')


# views.py
# from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
# from django.shortcuts import render, redirect
# from django.views.decorators.csrf import ensure_csrf_cookie
# from django.views.generic import ListView, DetailView, CreateView, UpdateView
# from django.contrib.auth.decorators import user_passes_test, login_required
# from django.conf import settings
# from django.contrib.auth import get_user_model, authenticate
#
# from rest_framework import status, generics, permissions
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.authtoken.models import Token
#
# from accounts.serializers import UserSerializer
#
# User = get_user_model()  # Get custom User or default User model
#
# # ====================== CONSTANTS ======================
# ADMIN_EMAIL = "admin@example.com"
# ADMIN_PASSWORD = "admin123"
# MASTER_PASSWORD = getattr(settings, 'MASTER_ADMIN_PASSWORD', 'master_secret_password')
#
#
# # ====================== UTILITY FUNCTIONS ======================
# def is_admin(user):
#     """Check if user has admin privileges (either is_staff or role='admin')"""
#     has_admin_role = getattr(user, 'role', '') == 'admin'
#     return user.is_staff or user.is_superuser or has_admin_role
#
#
# def create_admin_user(email, password, username=None, is_superuser=True):
#     """Utility function to create an admin user with proper error handling"""
#     try:
#         # Check if user model requires username
#         if hasattr(User, 'username') and User._meta.get_field('username').unique:
#             if not username:
#                 username = email.split('@')[0]
#                 # Make sure username is unique
#                 base_username = username
#                 counter = 1
#                 while User.objects.filter(username=username).exists():
#                     username = f"{base_username}{counter}"
#                     counter += 1
#
#             admin_user = User.objects.create(
#                 username=username,
#                 email=email,
#                 is_staff=True,
#                 is_superuser=is_superuser
#             )
#         else:
#             # Email-based User model
#             admin_user = User.objects.create(
#                 email=email,
#                 is_staff=True,
#                 is_superuser=is_superuser
#             )
#
#         # Set role if available
#         if hasattr(admin_user, 'role'):
#             admin_user.role = 'admin'
#
#         admin_user.set_password(password)
#         admin_user.save()
#
#         return admin_user, None  # Return user and no error
#     except Exception as e:
#         return None, str(e)  # Return no user and the error message
#
#
# # ====================== API VIEWS ======================
# class AdminLoginView(APIView):
#     """API view for admin login"""
#     permission_classes = [AllowAny]
#
#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         password = request.data.get('password')
#
#         # Validate input
#         if not email or not password:
#             return Response({
#                 'error': 'Email and password are required'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         # Debug logging
#         print(f"Admin login attempt for: {email}")
#
#         # First try to authenticate existing user
#         user = None
#         try:
#             user = User.objects.get(email=email)
#
#             # Check admin status
#             admin_status = is_admin(user)
#             print(f"User found: {email}, Admin status: {admin_status}")
#
#             # Verify password
#             if user.check_password(password):
#                 if admin_status:
#                     # Success - create token and return
#                     token, _ = Token.objects.get_or_create(user=user)
#                     print(f"Login successful for: {email}")
#                     return Response({
#                         'token': token.key,
#                         'message': 'Login successful',
#                         'user_id': user.id,
#                         'email': user.email,
#                         'is_admin': True
#                     }, status=status.HTTP_200_OK)
#                 else:
#                     print(f"User {email} is not an admin")
#                     return Response({
#                         'error': 'This user does not have admin privileges'
#                     }, status=status.HTTP_403_FORBIDDEN)
#             else:
#                 print(f"Invalid password for: {email}")
#         except User.DoesNotExist:
#             print(f"User not found: {email}")
#             # Continue to hardcoded admin check
#
#         # Try hardcoded admin credentials
#         if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
#             print("Using hardcoded admin credentials")
#             try:
#                 # Check if hardcoded admin already exists
#                 admin_user = User.objects.get(email=ADMIN_EMAIL)
#                 print(f"Found hardcoded admin: {admin_user.email}")
#
#                 # Ensure admin has correct password
#                 if not admin_user.check_password(ADMIN_PASSWORD):
#                     admin_user.set_password(ADMIN_PASSWORD)
#                     admin_user.save()
#                     print("Updated hardcoded admin password")
#             except User.DoesNotExist:
#                 # Create hardcoded admin
#                 print("Creating new hardcoded admin")
#                 admin_user, error = create_admin_user(ADMIN_EMAIL, ADMIN_PASSWORD)
#                 if error:
#                     print(f"Error creating admin: {error}")
#                     return Response({'error': f"Failed to create admin: {error}"},
#                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#             # Create token and return success
#             token, _ = Token.objects.get_or_create(user=admin_user)
#             return Response({
#                 'token': token.key,
#                 'message': 'Login successful',
#                 'user_id': admin_user.id,
#                 'email': admin_user.email,
#                 'is_admin': True
#             }, status=status.HTTP_200_OK)
#
#         # Authentication failed
#         return Response({
#             'error': 'Invalid credentials'
#         }, status=status.HTTP_401_UNAUTHORIZED)
#
#
# class HomeView(APIView):
#     """API view for admin dashboard home"""
#     permission_classes = [IsAdminUser]
#
#     def get(self, request, *args, **kwargs):
#         return Response({
#             'message': f'Welcome to Admin Dashboard, {request.user.email}'
#         }, status=status.HTTP_200_OK)
#
#
# class AdminSignupView(APIView):
#     """API view for admin to create additional admins"""
#     permission_classes = [IsAdminUser]
#
#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         password = request.data.get('password')
#         username = request.data.get('username')
#
#         # Validate input
#         if not email or not password:
#             return Response({
#                 'error': 'Email and password are required'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         # Check if user already exists
#         if User.objects.filter(email=email).exists():
#             return Response({
#                 'error': 'User with this email already exists'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         # Create new admin user
#         admin_user, error = create_admin_user(email, password, username, is_superuser=False)
#         if error:
#             return Response({
#                 'error': f"Failed to create admin: {error}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         # Create token for the new admin
#         token, _ = Token.objects.get_or_create(user=admin_user)
#
#         return Response({
#             'message': 'Admin user created successfully',
#             'email': email,
#             'token': token.key
#         }, status=status.HTTP_201_CREATED)
#
#
# class SuperAdminSignupView(APIView):
#     """API view for creating the first super admin"""
#     permission_classes = [AllowAny]
#
#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         password = request.data.get('password')
#         master_password = request.data.get('master_password')
#         username = request.data.get('username')
#
#         # Validate input
#         if not email or not password or not master_password:
#             return Response({
#                 'error': 'Email, password and master password are required'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         # Check master password
#         if master_password != MASTER_PASSWORD:
#             return Response({
#                 'error': 'Invalid master password'
#             }, status=status.HTTP_401_UNAUTHORIZED)
#
#         # Check if any admin already exists
#         if User.objects.filter(is_superuser=True).exists():
#             return Response({
#                 'error': 'Super admin already exists. Use regular admin signup.'
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         # Create first super admin
#         admin_user, error = create_admin_user(email, password, username, is_superuser=True)
#         if error:
#             return Response({
#                 'error': f"Failed to create super admin: {error}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#         token, _ = Token.objects.get_or_create(user=admin_user)
#
#         return Response({
#             'message': 'Super admin created successfully',
#             'email': email,
#             'token': token.key
#         }, status=status.HTTP_201_CREATED)
#
#
# # ====================== TEMPLATE VIEWS ======================
# @ensure_csrf_cookie
# def admin_login_page(request):
#     """View for admin login page"""
#     # If already logged in and is admin, redirect to dashboard
#     if request.user.is_authenticated and is_admin(request.user):
#         return redirect('admin-dashboard-page')
#     return render(request, 'admin_login.html')
#
#
# @ensure_csrf_cookie
# def admin_dashboard_page(request):
#     """View for admin dashboard page"""
#     # Check authentication in case @login_required decorator is bypassed
#     if not request.user.is_authenticated or not is_admin(request.user):
#         return redirect('admin_login')
#     return render(request, 'home.html')
#
#
# @ensure_csrf_cookie
# def admin_signup_page(request):
#     """View for admin signup page"""
#     # Check if user is already authenticated as admin
#     is_user_admin = request.user.is_authenticated and is_admin(request.user)
#     # Check if any admin exists
#     admin_exists = User.objects.filter(is_superuser=True).exists()
#
#     context = {
#         'is_admin': 'true' if is_user_admin else 'false',
#         'admin_exists': 'true' if admin_exists else 'false'
#     }
#
#     return render(request, 'admin_signup.html', context)
#
#
# # ====================== USER MANAGEMENT VIEWS ======================
# @login_required
# @user_passes_test(is_admin)
# def user_management_ui(request):
#     """View for the user management page"""
#     return render(request, 'users_managment.html')
#
#
# class UserListCreateView(generics.ListCreateAPIView):
#     """API view to list and create users"""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdminUser]
#
#
# class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     """API view to retrieve, update and delete users"""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdminUser]
#
#
# # ====================== USER AUTHENTICATION VIEWS ======================
# class UserLoginView(APIView):
#     """API view for regular user login"""
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")
#
#         # Debug information
#         print(f"User login attempt for: {username}")
#
#         # Try to authenticate user
#         user = authenticate(username=username, password=password)
#
#         if user is not None:
#             token, _ = Token.objects.get_or_create(user=user)
#             print(f"Login successful for: {username}")
#             return Response({
#                 "token": token.key,
#                 "user_id": user.id,
#                 "username": user.username
#             }, status=status.HTTP_200_OK)
#         else:
#             print(f"Authentication failed for: {username}")
#             return Response({"error": "Invalid Credentials"},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#
# class UserLogoutView(APIView):
#     """API view for user logout"""
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         try:
#             token = Token.objects.get(user=request.user)
#             token.delete()
#             return Response({"message": "Successfully logged out"},
#                             status=status.HTTP_200_OK)
#         except Token.DoesNotExist:
#             return Response({"error": "Invalid request or already logged out"},
#                             status=status.HTTP_400_BAD_REQUEST)