from django.db import connection
from rest_framework.generics import (CreateAPIView)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework.views import APIView
from .serializers import EmailRegistrationSerializer, PhoneRegistrationSerializer


class EmailRegistrationView(CreateAPIView):
    serializer_class = EmailRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_data = {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }

            return Response({
                "user": user_data,
                "access_token": access_token,
                "refresh_token": str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneRegistrationView(CreateAPIView):
    serializer_class = PhoneRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Убедимся, что в запросе есть только номер телефона
        phone_data = {'phone_number': request.data.get('phone_number')}

        serializer = self.get_serializer(data=request.data)  # Используем оригинальные данные запроса
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Получаем информацию о пользователе из сериализатора
            user_data = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }

            # Добавляем номер телефона из запроса (так как в модели пользователя его может не быть)
            if 'phone_number' in request.data:
                user_data["phone_number"] = request.data['phone_number']

            return Response({
                "user": user_data,
                "access_token": access_token,
                "refresh_token": str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"message": "User logout"}, status=status.HTTP_205_RESET_CONTENT)
            else:
                return Response({"error": "Need "}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Получаем все токены пользователя
            tokens = OutstandingToken.objects.filter(user=request.user)
            for token in tokens:
                # Проверяем, не заблокирован ли токен уже
                if not BlacklistedToken.objects.filter(token=token).exists():
                    BlacklistedToken.objects.create(token=token)

            return Response({"message": "Успешный выход из всех устройств"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatabaseConnectionCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Attempt to execute a simple query
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            return Response({
                "status": "success",
                "message": "Successfully connected to the database",
                "connection_info": {
                    "database_name": connection.settings_dict['NAME'],
                    "database_engine": connection.settings_dict['ENGINE'],
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # If there was an error connecting to the database
            return Response({
                "status": "error",
                "message": "Failed to connect to database",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
