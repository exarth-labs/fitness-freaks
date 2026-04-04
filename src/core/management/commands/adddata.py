import random
from datetime import timedelta, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from src.services.accounts.models import Instructor, UserType
from src.services.finance.models import (
    SubscriptionPlan, Member, Payment, Expense, GymShift,
    GenderChoice, PaymentMethodChoice, SubscriptionStatus,
    PaymentStatus, ExpenseCategory,
)
from src.apps.whisper.models import EmailNotification

fake = Faker(['en_US'])
User = get_user_model()


# ── helpers ──────────────────────────────────────────────────────────────────

def _phone():
    prefixes = ['300','301','302','303','311','312','313','321','322','333','334']
    p = random.choice(prefixes)
    n = ''.join(str(random.randint(0, 9)) for _ in range(7))
    return f"03{p[1]}{p[2]}{n}"


def _cnic():
    p1 = ''.join(str(random.randint(0, 9)) for _ in range(5))
    p2 = ''.join(str(random.randint(0, 9)) for _ in range(7))
    p3 = str(random.randint(0, 9))
    return f"{p1}-{p2}-{p3}"


def _unique_email(first, last):
    domain = random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 9999)}@{domain}"
    while User.objects.filter(email=email).exists():
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 99999)}@{domain}"
    return email


# ── seeders ──────────────────────────────────────────────────────────────────

def seed_shifts():
    defaults = [
        {'name': 'Morning Men',  'gender': GenderChoice.MALE,   'start_time': time(8, 0),  'end_time': time(10, 0)},
        {'name': 'Women',        'gender': GenderChoice.FEMALE, 'start_time': time(10, 0), 'end_time': time(14, 0)},
        {'name': 'Evening Men',  'gender': GenderChoice.MALE,   'start_time': time(14, 0), 'end_time': time(23, 0)},
    ]
    created = 0
    for d in defaults:
        _, c = GymShift.objects.get_or_create(name=d['name'], defaults=d)
        if c:
            created += 1
    return created


def seed_plans():
    plans_data = [
        {'name': 'Daily Pass',       'duration_days': 1,   'price': Decimal('500'),   'has_personal_trainer': False, 'has_locker': False},
        {'name': 'Weekly Basic',     'duration_days': 7,   'price': Decimal('2000'),  'has_personal_trainer': False, 'has_locker': False},
        {'name': 'Monthly Basic',    'duration_days': 30,  'price': Decimal('5000'),  'has_personal_trainer': False, 'has_locker': False},
        {'name': 'Monthly Premium',  'duration_days': 30,  'price': Decimal('8000'),  'has_personal_trainer': True,  'has_locker': True},
        {'name': 'Quarterly Basic',  'duration_days': 90,  'price': Decimal('12000'), 'has_personal_trainer': False, 'has_locker': True},
        {'name': 'Quarterly Premium','duration_days': 90,  'price': Decimal('20000'), 'has_personal_trainer': True,  'has_locker': True},
        {'name': 'Half Yearly',      'duration_days': 180, 'price': Decimal('25000'), 'has_personal_trainer': False, 'has_locker': True},
        {'name': 'Annual Membership','duration_days': 365, 'price': Decimal('45000'), 'has_personal_trainer': True,  'has_locker': True},
        {'name': 'Student Monthly',  'duration_days': 30,  'price': Decimal('3500'),  'has_personal_trainer': False, 'has_locker': False},
        {'name': 'Couple Monthly',   'duration_days': 30,  'price': Decimal('9000'),  'has_personal_trainer': False, 'has_locker': True},
    ]
    created = 0
    for d in plans_data:
        _, c = SubscriptionPlan.objects.get_or_create(name=d['name'], defaults=d)
        if c:
            created += 1
    return created


def seed_instructors(count=5):
    specializations = [
        'Weight Training', 'Cardio & Endurance', 'Boxing & Martial Arts',
        'Yoga & Flexibility', 'CrossFit', 'Nutrition & Diet',
        'Powerlifting', 'Functional Fitness',
    ]
    instructors = []
    for _ in range(count):
        first = fake.first_name_male()
        last = fake.last_name()
        email = _unique_email(first, last)
        username = f"{first.lower()}.{last.lower()}{random.randint(1, 9999)}"
        while User.objects.filter(username=username).exists():
            username = f"{first.lower()}.{last.lower()}{random.randint(1, 99999)}"
        user = User.objects.create_user(
            username=username,
            email=email,
            password='password123',
            first_name=first,
            last_name=last,
            user_type=UserType.administration,
            is_staff=True,
            is_active=True,
        )
        instructor = Instructor.objects.create(
            user=user,
            specialization=random.choice(specializations),
            hire_date=timezone.now().date() - timedelta(days=random.randint(30, 730)),
            bio=fake.paragraph(nb_sentences=2),
            is_active=True,
        )
        instructors.append(instructor)
    return instructors


def seed_members(count=50):
    plans = list(SubscriptionPlan.objects.all())
    shifts = list(GymShift.objects.all())
    instructors = list(Instructor.objects.filter(is_active=True))
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    health_conditions = [
        None, None, None, None,
        'Mild asthma', 'Previous knee injury', 'Diabetic - Type 2',
        'High blood pressure', 'Lower back pain',
    ]

    members = []
    today = timezone.now().date()

    for _ in range(count):
        gender = random.choice(['male', 'female'])
        if gender == 'male':
            first = fake.first_name_male()
        else:
            first = fake.first_name_female()
        last = fake.last_name()
        email = _unique_email(first, last)

        username = f"{first.lower()}.{last.lower()}{random.randint(1, 9999)}"
        while User.objects.filter(username=username).exists():
            username = f"{first.lower()}.{last.lower()}{random.randint(1, 99999)}"
        user = User.objects.create_user(
            username=username,
            email=email,
            password='password123',
            first_name=first,
            last_name=last,
            user_type=UserType.client,
            is_active=True,
        )

        plan = random.choice(plans)
        join_date = today - timedelta(days=random.randint(0, 365))
        sub_start = join_date
        sub_end = sub_start + timedelta(days=plan.duration_days)

        if sub_end < today:
            status = SubscriptionStatus.EXPIRED
        elif random.random() < 0.08:
            status = SubscriptionStatus.PENDING
        else:
            status = SubscriptionStatus.ACTIVE
            sub_end = today + timedelta(days=random.randint(1, plan.duration_days))

        # Pick gender-appropriate shift
        gender_shifts = [s for s in shifts if s.gender in (gender, GenderChoice.BOTH)] if shifts else []
        shift = random.choice(gender_shifts) if gender_shifts else None
        instructor = random.choice(instructors) if instructors and random.random() < 0.4 else None

        member = Member.objects.create(
            user=user,
            subscription_plan=plan,
            gender=gender,
            shift=shift,
            instructor=instructor,
            cnic=_cnic(),
            phone_number=_phone(),
            emergency_contact_name=fake.name(),
            emergency_contact_phone=_phone(),
            blood_group=random.choice(blood_groups),
            health_conditions=random.choice(health_conditions),
            weight=Decimal(str(round(random.uniform(50, 120), 1))),
            height=Decimal(str(round(random.uniform(150, 195), 1))),
            subscription_start=sub_start,
            subscription_end=sub_end,
            status=status,
            join_date=join_date,
            is_active=True,
        )
        members.append(member)
    return members


def seed_payments(count=120):
    members = list(Member.objects.select_related('subscription_plan').all())
    staff = list(User.objects.filter(is_staff=True))
    if not members:
        return 0

    payment_methods = list(PaymentMethodChoice.values)
    created = 0

    for _ in range(count):
        member = random.choice(members)
        plan = member.subscription_plan or random.choice(SubscriptionPlan.objects.all())
        payment_date = timezone.now() - timedelta(days=random.randint(0, 365), hours=random.randint(8, 20))
        status = random.choices(
            [PaymentStatus.PAID, PaymentStatus.PENDING, PaymentStatus.FAILED],
            weights=[85, 10, 5]
        )[0]
        discount = Decimal(str(random.choice([0, 0, 0, 500, 1000, 1500, 2000])))
        method = random.choice(payment_methods)
        ref = ''.join(str(random.randint(0, 9)) for _ in range(12)) if method != PaymentMethodChoice.CASH else None

        Payment.objects.create(
            member=member,
            subscription_plan=plan,
            amount=plan.price,
            discount=discount,
            payment_method=method,
            payment_date=payment_date,
            reference_number=ref,
            status=status,
            period_start=payment_date.date(),
            period_end=payment_date.date() + timedelta(days=plan.duration_days),
            received_by=random.choice(staff) if staff else None,
        )
        created += 1
    return created


def seed_expenses(count=60):
    staff = list(User.objects.filter(is_staff=True))
    categories = list(ExpenseCategory.values)
    methods = list(PaymentMethodChoice.values)
    amount_ranges = {
        ExpenseCategory.RENT:        (50000, 150000),
        ExpenseCategory.UTILITIES:   (10000, 50000),
        ExpenseCategory.SALARIES:    (20000, 80000),
        ExpenseCategory.EQUIPMENT:   (5000, 200000),
        ExpenseCategory.MAINTENANCE: (2000, 30000),
        ExpenseCategory.MARKETING:   (5000, 50000),
        ExpenseCategory.SUPPLIES:    (1000, 15000),
        ExpenseCategory.OTHER:       (500, 10000),
    }
    descriptions = {
        ExpenseCategory.RENT:        ['Monthly gym rent', 'Building rent payment'],
        ExpenseCategory.UTILITIES:   ['Electricity bill', 'Water bill', 'Internet charges'],
        ExpenseCategory.SALARIES:    ['Staff salaries', 'Trainer salary', 'Receptionist salary'],
        ExpenseCategory.EQUIPMENT:   ['Treadmill purchase', 'Dumbbell set', 'Bench press equipment'],
        ExpenseCategory.MAINTENANCE: ['AC servicing', 'Treadmill belt replacement', 'Plumbing repair'],
        ExpenseCategory.MARKETING:   ['Facebook ads', 'Flyer printing', 'Instagram promotion'],
        ExpenseCategory.SUPPLIES:    ['Towels purchase', 'Cleaning supplies', 'Hand sanitizers'],
        ExpenseCategory.OTHER:       ['Miscellaneous', 'First aid kit', 'Office supplies'],
    }
    recurring_cats = {ExpenseCategory.RENT, ExpenseCategory.UTILITIES, ExpenseCategory.SALARIES}

    for _ in range(count):
        cat = random.choice(categories)
        lo, hi = amount_ranges.get(cat, (1000, 10000))
        Expense.objects.create(
            category=cat,
            amount=Decimal(str(random.randint(lo, hi))),
            description=random.choice(descriptions.get(cat, ['General expense'])),
            expense_date=timezone.now().date() - timedelta(days=random.randint(0, 365)),
            payment_method=random.choice(methods),
            added_by=random.choice(staff) if staff else None,
            is_recurring=cat in recurring_cats,
        )
    return count


def seed_notifications(count=40):
    users = list(User.objects.all())
    if not users:
        return 0
    subjects = [
        'Welcome to Fitness Freak!',
        'Your subscription is expiring soon',
        'Payment received – Thank you!',
        'Renew your membership today',
        'Gym schedule update',
    ]
    statuses = ['pending', 'sent', 'sent', 'sent', 'failed']
    for _ in range(count):
        user = random.choice(users)
        EmailNotification.objects.create(
            subject=random.choice(subjects),
            body=fake.paragraph(nb_sentences=4),
            recipient=user.email,
            status=random.choice(statuses),
            failed_attempts=random.randint(0, 2),
        )
    return count


# ── command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Seed the database with realistic fake data for development.'

    def add_arguments(self, parser):
        parser.add_argument('--members', type=int, default=50, help='Number of members to create (default: 50)')
        parser.add_argument('--payments', type=int, default=120, help='Number of payments (default: 120)')
        parser.add_argument('--expenses', type=int, default=60, help='Number of expenses (default: 60)')
        parser.add_argument('--instructors', type=int, default=5, help='Number of instructors (default: 5)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n  FITNESS FREAKS — Adding Fake Data\n'))

        # Shifts
        n = seed_shifts()
        self.stdout.write(f'  Shifts      → {n} created  ({GymShift.objects.count()} total)')

        # Plans
        n = seed_plans()
        self.stdout.write(f'  Plans       → {n} created  ({SubscriptionPlan.objects.count()} total)')

        # Instructors
        instructors = seed_instructors(options['instructors'])
        self.stdout.write(f'  Instructors → {len(instructors)} created  ({Instructor.objects.count()} total)')

        # Members
        members = seed_members(options['members'])
        self.stdout.write(f'  Members     → {len(members)} created  ({Member.objects.count()} total)')

        # Payments
        n = seed_payments(options['payments'])
        self.stdout.write(f'  Payments    → {n} created  ({Payment.objects.count()} total)')

        # Expenses
        n = seed_expenses(options['expenses'])
        self.stdout.write(f'  Expenses    → {n} created  ({Expense.objects.count()} total)')

        # Notifications
        n = seed_notifications(40)
        self.stdout.write(f'  Emails      → {n} created  ({EmailNotification.objects.count()} total)')

        self.stdout.write(self.style.SUCCESS('\n  Done. Default password for all seeded users: password123\n'))
