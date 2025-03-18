# serializers.py
from rest_framework import serializers
from .models import Farm, Motor, Valve


class ValveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valve
        fields = '__all__'


class MotorSerializer(serializers.ModelSerializer):
    valves = ValveSerializer(many=True, read_only=True)

    class Meta:
        model = Motor
        fields = '__all__'


class FarmSerializer(serializers.ModelSerializer):
    motors = MotorSerializer(many=True, read_only=True)
    class Meta:
        model = Farm
        fields = '__all__'


