# serializers.py
from rest_framework import serializers

from accounts.models import User
from .models import Farm


class FarmSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(write_only=True, required=False)
    owner_details = serializers.SerializerMethodField()

    class Meta:
        model = Farm
        fields = ['id', 'name', 'location', 'size', 'description', 'created_at', 'updated_at',
                  'owner', 'owner_email', 'owner_details']
        read_only_fields = ['owner', 'owner_details']

    def get_owner_details(self, obj):
        return {
            'id': obj.owner.id,
            'email': obj.owner.email,
            'username': obj.owner.username,
            'role': obj.owner.role
        }

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        # Handle owner_email if provided by admin/manager
        if 'owner_email' in validated_data and user.role in ['admin', 'manager']:
            owner_email = validated_data.pop('owner_email')
            try:
                owner = User.objects.get(email=owner_email)
                validated_data['owner'] = owner
            except User.DoesNotExist:
                raise serializers.ValidationError({'owner_email': 'User with this email does not exist'})
        else:
            validated_data['owner'] = user

        return super().create(validated_data)