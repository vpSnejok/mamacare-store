# models.py
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return (
                not self.is_used and
                self.created_at + timedelta(hours=24) > timezone.now()
        )

    def __str__(self):
        return f"Token for {self.user.username} - {'Used' if self.is_used else 'Active'}"