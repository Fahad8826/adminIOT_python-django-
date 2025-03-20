# # serializers.py
# from rest_framework import serializers
# from .models import Motor, Valve
#
#
# class ValveSerializer(serializers.ModelSerializer):
#     status_display = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Valve
#         fields = ['valve_number', 'value', 'status_display', 'last_operated_at']
#
#     def get_status_display(self, obj):
#         return "On" if obj.value == "1" else "Off"
#
#
# class MotorSerializer(serializers.ModelSerializer):
#     valves = ValveSerializer(many=True, read_only=True)
#     # These fields will be used to create valves but won't be stored directly in the Motor model
#     V1 = serializers.CharField(write_only=True, required=False, default="0")
#     V2 = serializers.CharField(write_only=True, required=False, default="0")
#     V3 = serializers.CharField(write_only=True, required=False, default="0")
#
#     class Meta:
#         model = Motor
#         fields = ['id', 'name', 'UIN', 'TYPE', 'VCOUNT', 'STATUS', 'LOCATION',
#                   'V1', 'V2', 'V3', 'valves', 'created_at', 'updated_at']
#         read_only_fields = ['id', 'created_at', 'updated_at']
#
#     def create(self, validated_data):
#         # Extract valve data
#         v1 = validated_data.pop('V1', "0")
#         v2 = validated_data.pop('V2', "0")
#         v3 = validated_data.pop('V3', "0")
#
#         # Create the motor
#         motor = Motor.objects.create(**validated_data)
#
#         # Create valves based on VCOUNT
#         vcount = int(validated_data.get('VCOUNT', 0))
#         valve_values = [v1, v2, v3]
#
#         for i in range(vcount):
#             if i < len(valve_values):
#                 Valve.objects.create(
#                     motor=motor,
#                     valve_number=i + 1,
#                     value=valve_values[i]
#                 )
#
#         return motor
#
#     def update(self, instance, validated_data):
#         # Extract valve data
#         v1 = validated_data.pop('V1', None)
#         v2 = validated_data.pop('V2', None)
#         v3 = validated_data.pop('V3', None)
#
#         # Update the motor instance
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         # Update existing valves or create new ones
#         valve_values = {1: v1, 2: v2, 3: v3}
#         vcount = int(validated_data.get('VCOUNT', instance.VCOUNT))
#
#         # Update existing valves
#         for i in range(1, vcount + 1):
#             if i in valve_values and valve_values[i] is not None:
#                 valve, created = Valve.objects.update_or_create(
#                     motor=instance,
#                     valve_number=i,
#                     defaults={'value': valve_values[i]}
#                 )
#
#         # Remove extra valves if VCOUNT was reduced
#         Valve.objects.filter(motor=instance, valve_number__gt=vcount).delete()
#
#         return instance


# serializers.py
from rest_framework import serializers
from .models import Motor, Valve


class ValveSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Valve
        fields = ['valve_number', 'value', 'status_display', 'last_operated_at']

    def get_status_display(self, obj):
        return "On" if obj.value == "1" else "Off"


class MotorSerializer(serializers.ModelSerializer):
    valves = ValveSerializer(many=True, read_only=True)
    # These fields are optional for creating specific valve values
    V1 = serializers.CharField(write_only=True, required=False, default="0")
    V2 = serializers.CharField(write_only=True, required=False, default="0")
    V3 = serializers.CharField(write_only=True, required=False, default="0")
    V4 = serializers.CharField(write_only=True, required=False, default="0")
    V5 = serializers.CharField(write_only=True, required=False, default="0")
    V6 = serializers.CharField(write_only=True, required=False, default="0")
    V7 = serializers.CharField(write_only=True, required=False, default="0")
    V8 = serializers.CharField(write_only=True, required=False, default="0")
    V9 = serializers.CharField(write_only=True, required=False, default="0")
    V10 = serializers.CharField(write_only=True, required=False, default="0")

    class Meta:
        model = Motor
        fields = ['id', 'name', 'UIN', 'TYPE', 'VCOUNT', 'STATUS', 'LOCATION',
                  'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
                  'valves', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Extract valve data
        valve_data = {}
        for i in range(1, 11):
            key = f'V{i}'
            if key in validated_data:
                valve_data[i] = validated_data.pop(key)

        # Create the motor
        motor = Motor.objects.create(**validated_data)

        # Create valves based on VCOUNT - ensure all valves up to VCOUNT are created
        vcount = int(validated_data.get('VCOUNT', 0))

        for i in range(1, vcount + 1):
            value = valve_data.get(i, "0")  # Default to "0" if not specified
            Valve.objects.create(
                motor=motor,
                valve_number=i,
                value=value
            )

        return motor

    def update(self, instance, validated_data):
        # Extract valve data
        valve_data = {}
        for i in range(1, 11):
            key = f'V{i}'
            if key in validated_data:
                valve_data[i] = validated_data.pop(key)

        # Update the motor instance
        old_vcount = instance.VCOUNT
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Get the new VCOUNT
        new_vcount = instance.VCOUNT

        # Update existing valves or create new ones
        for i in range(1, new_vcount + 1):
            if i in valve_data:
                valve, created = Valve.objects.update_or_create(
                    motor=instance,
                    valve_number=i,
                    defaults={'value': valve_data[i]}
                )

        # Create any missing valves if VCOUNT was increased
        existing_valve_numbers = set(Valve.objects.filter(motor=instance).values_list('valve_number', flat=True))
        for i in range(1, new_vcount + 1):
            if i not in existing_valve_numbers:
                value = valve_data.get(i, "0")  # Default to "0" if not specified
                Valve.objects.create(
                    motor=instance,
                    valve_number=i,
                    value=value
                )

        # Remove extra valves if VCOUNT was reduced
        if new_vcount < old_vcount:
            Valve.objects.filter(motor=instance, valve_number__gt=new_vcount).delete()

        return instance