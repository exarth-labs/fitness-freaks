#!/usr/bin/env python
"""
Clean Data Script for Fitness Freaks Gym Management App
Removes ALL data except the first superuser and subscription plans.

Usage:
    python docs/bash/clean_data.py

Or with force flag (skip confirmation):
    python docs/bash/clean_data.py --force
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
django.setup()

from django.contrib.auth import get_user_model
from src.services.finance.models import Member, Payment, Expense, SubscriptionPlan
from src.apps.whisper.models import EmailNotification

User = get_user_model()


def main():
    print("=" * 60)
    print("🧹 FITNESS FREAKS - DATA CLEANER")
    print("=" * 60)

    # Confirmation unless --force is used
    if '--force' not in sys.argv:
        print("\n⚠️  WARNING: This will delete ALL data from the database!")
        print("   The following will be kept:")
        print("   • First superuser account")
        print("   • Subscription plans")
        print("\n   The following will be DELETED:")
        print("   • All users (except first superuser)")
        print("   • All members")
        print("   • All payments")
        print("   • All expenses")
        print("   • All email notifications")
        
        confirm = input("\n   Type 'YES' to continue: ")
        if confirm != 'YES':
            print("   ❌ Cancelled.")
            return

    print("\n🗑️  Cleaning data...")

    # Delete in correct order (respecting foreign keys)
    email_count, _ = EmailNotification.objects.all().delete()
    print(f"   • Email Notifications: {email_count} deleted")

    payment_count, _ = Payment.objects.all().delete()
    print(f"   • Payments: {payment_count} deleted")

    expense_count, _ = Expense.objects.all().delete()
    print(f"   • Expenses: {expense_count} deleted")

    member_count, _ = Member.objects.all().delete()
    print(f"   • Members: {member_count} deleted")

    # Delete all users except the first superuser
    first_superuser = User.objects.filter(is_superuser=True).order_by('date_joined').first()
    if first_superuser:
        deleted_count, _ = User.objects.exclude(id=first_superuser.id).delete()
        print(f"   • Users: {deleted_count} deleted (kept: {first_superuser.email})")
    else:
        deleted_count, _ = User.objects.all().delete()
        print(f"   • Users: {deleted_count} deleted (no superuser found)")

    # Subscription plans are kept
    plan_count = SubscriptionPlan.objects.count()
    print(f"   • Subscription Plans: {plan_count} kept")

    # Summary
    print("\n" + "=" * 60)
    print("✅ DATA CLEANED SUCCESSFULLY!")
    print("=" * 60)

    if first_superuser:
        print(f"""
📊 Remaining Data:
   • Superuser: {first_superuser.email}
   • Subscription Plans: {SubscriptionPlan.objects.count()}
   • Members: {Member.objects.count()}
   • Payments: {Payment.objects.count()}
   • Expenses: {Expense.objects.count()}
   • Email Notifications: {EmailNotification.objects.count()}
""")
    else:
        print("""
⚠️  No superuser found! Create one with:
   python manage.py createsuperuser
""")


if __name__ == '__main__':
    main()
