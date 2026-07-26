from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "desired_position", "city",
            "min_salary", "skills", "telegram_username",
        ]
        read_only_fields = ["id"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["username", "email", "password", "desired_position", "city",
                  "min_salary", "skills"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        attrs["user"] = user
        return attrs


class TelegramLinkSerializer(serializers.Serializer):
    """Used by the internal /telegram-link/ endpoint that the bot calls
    after the user shares their Telegram contact via /start."""

    username = serializers.CharField()
    telegram_chat_id = serializers.IntegerField()
    telegram_username = serializers.CharField(required=False, allow_blank=True)
