from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Payment, Member, SubscriptionStatus, PaymentStatus


@receiver(post_save, sender=Payment)
def update_member_on_payment(sender, instance, created, **kwargs):
    """
    Update member subscription status when a payment is made.
    Centralized logic to avoid duplication in Payment.save()
    """
    if not created:
        return

    if instance.status == PaymentStatus.PAID and instance.member and instance.subscription_plan:
        member = instance.member

        # Update subscription period dates
        if instance.period_start and instance.period_end:
            if not member.subscription_start or instance.period_start < member.subscription_start:
                member.subscription_start = instance.period_start
            if not member.subscription_end or instance.period_end > member.subscription_end:
                member.subscription_end = instance.period_end

            member.subscription_plan = instance.subscription_plan
            member.status = SubscriptionStatus.ACTIVE
            member.save(update_fields=['subscription_start', 'subscription_end', 'status', 'subscription_plan'])

