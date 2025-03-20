from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Motor(models.Model):
    TYPE_CHOICES = [
        ('REQ', 'Required'),
        ('OPT', 'Optional'),
    ]

    STATUS_CHOICES = [
        ('Working', 'Working'),
        ('Maintenance', 'Under Maintenance'),
        ('Failed', 'Failed'),
        ('Idle', 'Idle'),
    ]

    name = models.CharField(max_length=100)
    UIN = models.CharField(max_length=15, unique=True)
    TYPE = models.CharField(max_length=3, choices=TYPE_CHOICES, default='REQ')
    VCOUNT = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    STATUS = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Working')
    LOCATION = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.UIN}"

    class Meta:
        ordering = ['-created_at']


class Valve(models.Model):
    VALVE_STATUS_CHOICES = [
        ('0', 'Off'),
        ('1', 'On'),
    ]

    motor = models.ForeignKey(Motor, related_name='valves', on_delete=models.CASCADE)
    valve_number = models.PositiveIntegerField()
    value = models.CharField(max_length=10, choices=VALVE_STATUS_CHOICES, default="0")
    last_operated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('motor', 'valve_number')
        ordering = ['valve_number']

    def __str__(self):
        return f"Valve {self.valve_number} of Motor {self.motor.name}"

    def turn_on(self):
        """Turn the valve on"""
        self.value = "1"
        self.save()
        return True

    def turn_off(self):
        """Turn the valve off"""
        self.value = "0"
        self.save()
        return True