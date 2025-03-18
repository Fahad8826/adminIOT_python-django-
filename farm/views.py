from django.shortcuts import render
from rest_framework import generics
from .models import Farm, Motor, Valve
from .serializers import FarmSerializer, MotorSerializer, ValveSerializer
from rest_framework.permissions import IsAuthenticated

class FarmListCreateView(generics.ListCreateAPIView):
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Farm.objects.filter(user=self.request.user)

class FarmDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Farm.objects.filter(user=self.request.user)

class MotorListCreateView(generics.ListCreateAPIView):
    serializer_class = MotorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        farm_id = self.kwargs.get('farm_id')
        return Motor.objects.filter(farm_id=farm_id, farm__user=self.request.user)

class MotorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MotorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        farm_id = self.kwargs.get('farm_id')
        return Motor.objects.filter(farm_id=farm_id, farm__user=self.request.user)

class ValveListCreateView(generics.ListCreateAPIView):
    serializer_class = ValveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        motor_id = self.kwargs.get('motor_id')
        return Valve.objects.filter(motor_id=motor_id, motor__farm__user=self.request.user)

class ValveDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ValveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        motor_id = self.kwargs.get('motor_id')
        return Valve.objects.filter(motor_id=motor_id, motor__farm__user=self.request.user)
# -----------------------------html-------------------------------

# def farm_management(request, user_id=None):  # Add user_id as an optional argument
#     return render(request, 'farmCRUD.html', {'user_id': user_id})

def farm_management(request):  # Add user_id as an optional argument
    return render(request, 'farmCRUD.html', )
