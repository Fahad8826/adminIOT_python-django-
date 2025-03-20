# views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Motor, Valve
from .serializers import MotorSerializer, ValveSerializer


# Motor CRUD views
class MotorListCreateView(generics.ListCreateAPIView):
    queryset = Motor.objects.all()
    serializer_class = MotorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        motor = serializer.save()

        # Double-check that all valves are created
        vcount = motor.VCOUNT
        existing_valve_count = Valve.objects.filter(motor=motor).count()

        # Create missing valves if any
        if existing_valve_count < vcount:
            existing_valve_numbers = set(Valve.objects.filter(motor=motor).values_list('valve_number', flat=True))
            for i in range(1, vcount + 1):
                if i not in existing_valve_numbers:
                    Valve.objects.create(
                        motor=motor,
                        valve_number=i,
                        value="0"  # Default value
                    )

        # Return the full motor data including all valves
        result = self.get_serializer(motor)
        headers = self.get_success_headers(serializer.data)
        return Response(result.data, status=status.HTTP_201_CREATED, headers=headers)


class MotorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Motor.objects.all()
    serializer_class = MotorSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_vcount = instance.VCOUNT

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        motor = serializer.save()

        # Handle valve count changes
        new_vcount = motor.VCOUNT

        # Create any missing valves if VCOUNT was increased/changed
        existing_valve_numbers = set(Valve.objects.filter(motor=motor).values_list('valve_number', flat=True))
        for i in range(1, new_vcount + 1):
            if i not in existing_valve_numbers:
                Valve.objects.create(
                    motor=motor,
                    valve_number=i,
                    value="0"  # Default value
                )

        # Remove extra valves if VCOUNT was reduced
        if new_vcount < old_vcount:
            Valve.objects.filter(motor=motor, valve_number__gt=new_vcount).delete()

        # Return the updated motor data
        result = self.get_serializer(motor)
        return Response(result.data)


# Valve related views
class ValveListView(generics.ListAPIView):
    serializer_class = ValveSerializer

    def get_queryset(self):
        motor_id = self.kwargs.get('motor_id')
        return Valve.objects.filter(motor_id=motor_id)


class ValveAddView(APIView):
    def post(self, request, motor_id):
        try:
            motor = Motor.objects.get(pk=motor_id)
        except Motor.DoesNotExist:
            return Response({"error": "Motor not found"}, status=status.HTTP_404_NOT_FOUND)

        valve_number = request.data.get('valve_number')
        value = request.data.get('value', '0')

        if not valve_number:
            return Response({"error": "valve_number is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            valve_number = int(valve_number)
        except ValueError:
            return Response({"error": "valve_number must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if valve already exists
        if Valve.objects.filter(motor=motor, valve_number=valve_number).exists():
            return Response({"error": f"Valve {valve_number} already exists for this motor"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create new valve
        valve = Valve.objects.create(motor=motor, valve_number=valve_number, value=value)

        # Update VCOUNT if needed
        current_valve_count = Valve.objects.filter(motor=motor).count()
        if current_valve_count > motor.VCOUNT:
            motor.VCOUNT = current_valve_count
            motor.save()

        serializer = ValveSerializer(valve)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ValveControlView(APIView):
    def post(self, request, motor_id, valve_number):
        """Control (turn on/off) a specific valve of a motor"""
        try:
            motor = Motor.objects.get(pk=motor_id)
        except Motor.DoesNotExist:
            return Response({"error": "Motor not found"}, status=status.HTTP_404_NOT_FOUND)

        action_type = request.data.get('action', '').lower()

        try:
            valve = Valve.objects.get(motor=motor, valve_number=valve_number)
        except Valve.DoesNotExist:
            return Response(
                {"error": f"Valve {valve_number} does not exist for motor {motor.name}"},
                status=status.HTTP_404_NOT_FOUND
            )

        if action_type == 'on':
            valve.turn_on()
            return Response({"status": "success", "message": f"Valve {valve_number} turned ON"})
        elif action_type == 'off':
            valve.turn_off()
            return Response({"status": "success", "message": f"Valve {valve_number} turned OFF"})
        else:
            return Response(
                {"error": "Invalid action. Use 'on' or 'off'"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ValveStatusView(APIView):
    def get(self, request, motor_id):
        """Get the status of all valves for a motor"""
        try:
            motor = Motor.objects.get(pk=motor_id)
        except Motor.DoesNotExist:
            return Response({"error": "Motor not found"}, status=status.HTTP_404_NOT_FOUND)

        valves = Valve.objects.filter(motor=motor)

        status_data = {
            "motor_name": motor.name,
            "UIN": motor.UIN,
            "valve_count": motor.VCOUNT,
            "valves": {}
        }

        for valve in valves:
            status_data["valves"][f"V{valve.valve_number}"] = {
                "status": "On" if valve.value == "1" else "Off",
                "value": valve.value,
                "last_operated": valve.last_operated_at
            }

        return Response(status_data)


# views.py (partial - MotorListCreateView)
# from rest_framework import generics, status
# from rest_framework.response import Response
# from .models import Motor, Valve
# from .serializers import MotorSerializer
#
#
# class MotorListCreateView(generics.ListCreateAPIView):
#     queryset = Motor.objects.all()
#     serializer_class = MotorSerializer
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         motor = serializer.save()
#
#         # Double-check that all valves are created
#         vcount = motor.VCOUNT
#         existing_valve_count = Valve.objects.filter(motor=motor).count()
#
#         # Create missing valves if any
#         if existing_valve_count < vcount:
#             existing_valve_numbers = set(Valve.objects.filter(motor=motor).values_list('valve_number', flat=True))
#             for i in range(1, vcount + 1):
#                 if i not in existing_valve_numbers:
#                     Valve.objects.create(
#                         motor=motor,
#                         valve_number=i,
#                         value="0"  # Default value
#                     )
#
#         # Return the full motor data including all valves
#         result = self.get_serializer(motor)
#         headers = self.get_success_headers(serializer.data)
#         return Response(result.data, status=status.HTTP_201_CREATED, headers=headers)
#
#
# class MotorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Motor.objects.all()
#     serializer_class = MotorSerializer
#
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         old_vcount = instance.VCOUNT
#
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         motor = serializer.save()
#
#         # Handle valve count changes
#         new_vcount = motor.VCOUNT
#
#         # Create any missing valves if VCOUNT was increased/changed
#         existing_valve_numbers = set(Valve.objects.filter(motor=motor).values_list('valve_number', flat=True))
#         for i in range(1, new_vcount + 1):
#             if i not in existing_valve_numbers:
#                 Valve.objects.create(
#                     motor=motor,
#                     valve_number=i,
#                     value="0"  # Default value
#                 )
#
#         # Remove extra valves if VCOUNT was reduced
#         if new_vcount < old_vcount:
#             Valve.objects.filter(motor=motor, valve_number__gt=new_vcount).delete()
#
#         # Return the updated motor data
#         result = self.get_serializer(motor)
#         return Response(result.data)