from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    USER_ROLE = (
        (USER, 'User role'),
        (ADMIN, 'Administrator role'),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
    )
    password = models.CharField(
        max_length=150,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    is_subscribed = models.BooleanField(
        default=False,
    )
    role = models.CharField(
        max_length=15,
        choices=USER_ROLE,
        default=USER
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
