from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from todo_app.models import User, ToDo


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), username=username, password=password)
        if not user:
            msg = 'Unable to login with required credentials'
            raise ValidationError(msg)
        return user

    class Meta:
        model = User
        fields = ('username', 'password')


class ToDoListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }

    class Meta:
        model = ToDo
        fields = ('id', 'user', 'task_name', 'task_description', 'start_date', 'end_date', 'status', 'priority', 'is_active')


class ToDoAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = '__all__'
