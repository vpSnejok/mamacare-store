from django.contrib.auth.models import User
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class EmailRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class PhoneRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)


    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        # Для примера мы используем телефон как имя пользователя, но можно использовать и другой способ
        user = User.objects.create_user(
            username=validated_data['username'],  # Здесь это будет телефон
            password=validated_data['password']
        )
        return user
