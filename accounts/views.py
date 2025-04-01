from django.conf import settings
from django.db import connection
from django.utils.crypto import get_random_string
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.generics import (CreateAPIView)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework.views import APIView
from .serializers import EmailRegistrationSerializer, PhoneRegistrationSerializer, ChangePasswordSerializer, \
    success_change_response, PasswordResetRequestSerializer, PasswordResetConfirmSerializer


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

            return Response({"message": "Successfully logged out of all devices"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Authentication'],
        summary='Изменение пароля',
        description='Изменяет пароль авторизованного пользователя',
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Пароль успешно изменен',
                examples=[
                    OpenApiExample(
                        name='success',
                        value=success_change_response
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Неверные данные запроса',
                examples=[
                    OpenApiExample(
                        name='invalid_old_password',
                        value={'old_password': ['Неверный пароль']}
                    ),
                    OpenApiExample(
                        name='passwords_dont_match',
                        value={'confirm_password': ['Пароли не совпадают']}
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='change_password_example',
                value={
                    'old_password': 'current_password123',
                    'new_password': 'new_secure_password456',
                    'confirm_password': 'new_secure_password456'
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Проверяем старый пароль
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": ["Неверный пароль"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Устанавливаем новый пароль
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # Обновляем токены
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Пароль успешно изменен",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Запрос на сброс пароля',
        description='Отправляет на указанный email инструкции по сбросу пароля',
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Инструкции отправлены (если email зарегистрирован)',
                examples=[
                    OpenApiExample(
                        name='success',
                        value={
                            'message': 'Если указанный email зарегистрирован, инструкции по сбросу пароля были отправлены'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Неверные данные запроса',
                examples=[
                    OpenApiExample(
                        name='invalid_email',
                        value={'email': ['Введите правильный адрес электронной почты.']}
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='reset_password_request_example',
                value={
                    'email': 'user@example.com'
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)

                # Создаем уникальный токен
                token = get_random_string(64)

                # Сохраняем токен в базе
                PasswordResetToken.objects.create(
                    user=user,
                    token=token
                )

                # Отправляем email
                reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
                send_mail(
                    'Сброс пароля',
                    f'Для сброса пароля перейдите по ссылке: {reset_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

            except User.DoesNotExist:
                # По соображениям безопасности не указываем, что пользователь не найден
                pass

            # Всегда возвращаем успешный ответ
            return Response(
                {"message": "Если указанный email зарегистрирован, инструкции по сбросу пароля были отправлены"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Подтверждение сброса пароля',
        description='Устанавливает новый пароль с помощью токена, полученного по email',
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Пароль успешно изменен',
                examples=[
                    OpenApiExample(
                        name='success',
                        value=success_change_response
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Неверные данные запроса',
                examples=[
                    OpenApiExample(
                        name='invalid_token',
                        value={'token': ['Недействительный токен']}
                    ),
                    OpenApiExample(
                        name='expired_token',
                        value={'token': ['Токен недействителен или истек срок его действия']}
                    ),
                    OpenApiExample(
                        name='passwords_dont_match',
                        value={'confirm_password': ['Пароли не совпадают']}
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                name='reset_password_confirm_example',
                value={
                    'token': 'a1b2c3d4e5f6g7h8i9j0klmnopqrstuvwxyz1234567890abcdefghijklmn',
                    'new_password': 'new_secure_password456',
                    'confirm_password': 'new_secure_password456'
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token_str = serializer.validated_data['token']

            try:
                # Проверяем токен
                token_obj = PasswordResetToken.objects.get(token=token_str, is_used=False)

                if not token_obj.is_valid():
                    return Response(
                        {"token": ["Токен недействителен или истек срок его действия"]},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Меняем пароль
                user = token_obj.user
                user.set_password(serializer.validated_data['new_password'])
                user.save()

                # Помечаем токен как использованный
                token_obj.is_used = True
                token_obj.save()

                # Создаем новые токены аутентификации
                refresh = RefreshToken.for_user(user)

                return Response({
                    "message": "Пароль успешно изменен",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }, status=status.HTTP_200_OK)

            except PasswordResetToken.DoesNotExist:
                return Response(
                    {"token": ["Недействительный токен"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
