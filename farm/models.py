# models.py
from django.db import models
from django.conf import settings
from django.shortcuts import render


class Farm(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    area = models.FloatField(help_text="Area in acres")
    farm_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Motor(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='motors')
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100, blank=True)
    motor_type = models.CharField(max_length=50)
    horsepower = models.IntegerField()
    status = models.BooleanField(default=False)
    installed_date = models.DateField()
    last_maintenance = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.farm.name}"


class Valve(models.Model):
    motor = models.ForeignKey(Motor, on_delete=models.CASCADE, related_name='valves')
    name = models.CharField(max_length=100)
    valve_type = models.CharField(max_length=50)
    status = models.BooleanField(default=False)
    flow_rate = models.IntegerField(null=True, blank=True)
    connection_details = models.CharField(max_length=200, blank=True)
    installed_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.motor.name}"




