from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь."""
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='first name',
        blank=False
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='last name',
        blank=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
