from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework import viewsets
from .models import Farm, Motor, Valve
from .serializers import FarmSerializer, MotorSerializer, ValveSerializer


class FarmViewSet(viewsets.ModelViewSet):
    serializer_class = FarmSerializer

    def get_queryset(self):
        # Filter farms by the current user
        return Farm.objects.filter(user=self.request.user)


class MotorViewSet(viewsets.ModelViewSet):
    serializer_class = MotorSerializer

    def get_queryset(self):
        farm_id = self.kwargs.get('farm_pk')
        return Motor.objects.filter(farm_id=farm_id, farm__user=self.request.user)


class ValveViewSet(viewsets.ModelViewSet):
    serializer_class = ValveSerializer

    def get_queryset(self):
        motor_id = self.kwargs.get('motor_pk')
        return Valve.objects.filter(motor_id=motor_id, motor__farm__user=self.request.user)