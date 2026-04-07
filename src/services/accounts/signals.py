from django.db.models.signals import post_save
from django.dispatch import receiver
from src.services.accounts.models import User


@receiver(post_save, sender=User)
def assign_role_permissions(sender, instance, created, **kwargs):
    """
    Placeholder for future role-based permission assignment.
    Currently handled by Django's built-in permission system and admin.
    """
    pass
