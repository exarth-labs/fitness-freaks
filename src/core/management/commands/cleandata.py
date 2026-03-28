from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from src.services.accounts.models import Instructor
from src.services.finance.models import (
    Member, Payment, Expense, GymShift, SubscriptionPlan,
)
from src.apps.whisper.models import EmailNotification

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete all data except the first superuser. Keeps shifts and plans intact.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='delete_all',
            help='Also delete shifts and subscription plans',
        )

    def handle(self, *args, **options):
        if not options['yes']:
            self.stdout.write(self.style.WARNING(
                '\n  This will delete ALL data except the first superuser.\n'
                '  Run with --yes to confirm, or --all to also wipe shifts & plans.\n'
            ))
            confirm = input('  Type "yes" to continue: ').strip().lower()
            if confirm != 'yes':
                self.stdout.write('  Cancelled.')
                return

        self.stdout.write(self.style.MIGRATE_HEADING('\n  FITNESS FREAKS — Cleaning Data\n'))

        # Keep the first superuser
        first_super = User.objects.filter(is_superuser=True).order_by('date_joined').first()
        if first_super:
            self.stdout.write(f'  Keeping superuser: {first_super.email}')

        # Delete in FK-safe order
        n = EmailNotification.objects.all().delete()[0]
        self.stdout.write(f'  Email notifications  → deleted {n}')

        n = Payment.objects.all().delete()[0]
        self.stdout.write(f'  Payments             → deleted {n}')

        n = Member.objects.all().delete()[0]
        self.stdout.write(f'  Members              → deleted {n}')

        n = Instructor.objects.all().delete()[0]
        self.stdout.write(f'  Instructors          → deleted {n}')

        # Delete all users except the first superuser
        qs = User.objects.all()
        if first_super:
            qs = qs.exclude(pk=first_super.pk)
        n = qs.delete()[0]
        self.stdout.write(f'  Users                → deleted {n}')

        if options['delete_all']:
            n = SubscriptionPlan.objects.all().delete()[0]
            self.stdout.write(f'  Subscription plans   → deleted {n}')

            n = GymShift.objects.all().delete()[0]
            self.stdout.write(f'  Gym shifts           → deleted {n}')
        else:
            self.stdout.write(f'  Subscription plans   → kept ({SubscriptionPlan.objects.count()} records)')
            self.stdout.write(f'  Gym shifts           → kept ({GymShift.objects.count()} records)')

        self.stdout.write(self.style.SUCCESS('\n  Done.\n'))
