from rest_framework import serializers
from .models import RegisteredUser

class RegisteredUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredUser
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'is_admin']
