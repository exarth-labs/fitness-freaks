from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.apps.whisper.models import EmailNotification
from src.services.finance.models import Member, SubscriptionStatus


class Command(BaseCommand):
    help = 'Send email reminders to members whose subscription expires within 7 days'

    def handle(self, *args, **options):
        from src.apps.whisper.main import NotificationService

        today = timezone.now().date()
        week_later = today + timedelta(days=7)

        # Active members expiring within the next 7 days
        expiring = Member.objects.filter(
            status=SubscriptionStatus.ACTIVE,
            subscription_end__gte=today,
            subscription_end__lte=week_later,
            is_active=True,
        ).select_related('user', 'subscription_plan', 'shift')

        sent = 0
        skipped = 0

        for member in expiring:
            email = member.user.email

            # Avoid duplicates: skip if a reminder was already sent in the last 7 days
            already_sent = EmailNotification.objects.filter(
                recipient=email,
                subject__startswith='Gym Membership Expiring Soon',
                created_at__date__gte=today - timedelta(days=7),
                status='sent',
            ).exists()

            if already_sent:
                skipped += 1
                self.stdout.write(f'  Skipped (already sent): {email}')
                continue

            days_remaining = (member.subscription_end - today).days
            plan_name = member.subscription_plan.name if member.subscription_plan else 'N/A'
            shift_name = member.shift.name if member.shift else 'N/A'

            service = NotificationService(
                heading='Gym Membership Expiring Soon',
                description=f'Your gym membership expires on {member.subscription_end}. Please renew to continue.',
                obj=member,
            )

            service.send_email_notification_smtp(
                template='whisper/email/expiry_reminder.html',
                context={
                    'member_name': member.user.get_full_name() or member.user.email,
                    'expiry_date': member.subscription_end.strftime('%B %d, %Y'),
                    'days_remaining': days_remaining,
                    'plan_name': plan_name,
                    'shift_name': shift_name,
                },
                email=email,
            )
            sent += 1
            self.stdout.write(self.style.SUCCESS(f'  Sent reminder to: {email} (expires in {days_remaining} days)'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. Sent: {sent} | Skipped (duplicate): {skipped} | Total expiring: {expiring.count()}'
        ))
