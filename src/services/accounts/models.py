import re

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django_resized import ResizedImageField

from src.core.bll import get_action_urls
from src.core.models import phone_number_null_or_validator


class UserType(models.TextChoices):
    administration = 'administration', 'Administration'
    client = 'client', 'Client'


class GenderChoice(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'


def validate_pakistan_cnic(value):
    """Validate Pakistan CNIC format: 12345-1234567-1"""
    if value in [None, '']:
        return
    cnic_regex = r'^\d{5}-\d{7}-\d{1}$'
    if not re.match(cnic_regex, value):
        raise ValidationError(
            'CNIC must be in format: 12345-1234567-1 (5 digits, 7 digits, 1 digit)'
        )


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=200)
    profile_image = ResizedImageField(
        upload_to='accounts/images/profiles/', null=True, blank=True, size=[250, 250], quality=75, force_format='PNG',
        help_text='size of logo must be 250*250 and format must be png image file', crop=['middle', 'center']
    )
    phone_number = models.CharField(
        max_length=14, blank=True, null=True,
        validators=[phone_number_null_or_validator]
    )
    gender = models.CharField(
        max_length=10, choices=GenderChoice.choices, blank=True, null=True,
        help_text="User's gender (optional)"
    )
    cnic = models.CharField(
        max_length=15, blank=True, null=True, unique=True,
        validators=[validate_pakistan_cnic],
        help_text='CNIC Number (e.g., 12345-1234567-1) — optional, Pakistan only'
    )
    user_type = models.CharField(max_length=50, choices=UserType.choices, default=UserType.client)
    description = models.TextField(null=True, blank=True)

    REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = "email"

    allowed_actions = ['delete', 'detail', 'list']

    class Meta:
        ordering = ['-id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.get_full_name() or self.username or self.email

    def delete(self, *args, **kwargs):
        if self.profile_image:
            self.profile_image.delete(save=False)
        super().delete(*args, **kwargs)

    def get_display_fields(self):
        return ['id', 'first_name', 'last_name', 'email', 'platform', 'user_type', 'is_active', 'is_staff']

    def get_action_urls(self, user):
        return get_action_urls(self, user, True)

    def save(self, *args, **kwargs):
        if (self.is_staff or self.is_superuser) and self.user_type == UserType.client:
            self.user_type = UserType.administration

        super().save(*args, **kwargs)


""" INSTRUCTOR """


class Instructor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='instructor_profile'
    )
    specialization = models.CharField(
        max_length=100, help_text='e.g. Cardio, Weight Training, Boxing, Yoga'
    )
    hire_date = models.DateField(default=None, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    allowed_actions = ['delete', 'update', 'detail']

    class Meta:
        ordering = ['-created_on']
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructors'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} — {self.specialization}"

    def get_display_fields(self):
        return ['user', 'specialization', 'hire_date', 'is_active']

    def get_action_urls(self, user):
        return get_action_urls(self, user, True)
