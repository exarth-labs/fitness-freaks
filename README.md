# Fitness Freaks — Gym Management System

A Django-based gym management system for tracking members, subscriptions, payments, and expenses. Built for a single gym in Pakistan.

---

## Quick Start

### Option 1: Setup Script

```bash
chmod +x docs/bash/setup.sh && ./docs/bash/setup.sh
```

### Option 2: Manual

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp docs/configs/.env .env          # then fill in values
python manage.py makemigrations accounts core finance whisper
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Default dev login: `mark@exarth.com` / `mark` — admin at `/admin/`

---

## Environment Variables (`.env`)

| Variable | Description |
|---|---|
| `DEBUG` | `True` / `False` |
| `SECRET_KEY` | Django secret key |
| `ENVIRONMENT` | `local` (SQLite) or `server` (PostgreSQL) |
| `DOMAIN` | e.g. `localhost:8000` |
| `PROTOCOL` | `http` or `https` |
| `ALLOWED_HOSTS` | Comma-separated hosts |
| `SITE_ID` | Django site ID (usually `1`) |
| `TIME_ZONE` | e.g. `Asia/Karachi` |
| `DB_*` | PostgreSQL config (server only) |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP config |
| `DEFAULT_FROM_EMAIL` | Sender address |
| `MAILCHIMP_API_KEY` / `MAILCHIMP_FROM_EMAIL` | Mailchimp Transactional |

---

## Management Commands

### Development Data

```bash
# Seed with fake data (default: 50 members, 120 payments, 60 expenses, 5 instructors)
python manage.py adddata

# Customise counts
python manage.py adddata --members 100 --payments 200 --expenses 80 --instructors 8
```

Seeded users get password `password123`.

```bash
# Clean all data, keep first superuser, keep shifts & plans
python manage.py cleandata

# Also wipe shifts and subscription plans
python manage.py cleandata --all

# Skip confirmation prompt
python manage.py cleandata --yes
python manage.py cleandata --yes --all
```

### Notifications

```bash
# Send expiry reminder emails (members expiring within 7 days)
python manage.py send_expiry_reminders

# Recommended cron (runs daily at 9 AM)
# 0 9 * * * python manage.py send_expiry_reminders
```

### Standard Django

```bash
python manage.py makemigrations accounts core finance whisper
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py runserver
python manage.py shell
```

---

## Bash Scripts (`docs/bash/`)

```bash
chmod +x docs/bash/*.sh    # first time only

./docs/bash/setup.sh                # full project setup
./docs/bash/superuser.sh            # create superuser
./docs/bash/migrations_clean.sh     # wipe all migration files
./docs/bash/faker.sh                # legacy fake data script
```

---

## Apps

| App | Path | Description |
|---|---|---|
| `core` | `src/core/` | Shared mixins, template tags, base models |
| `accounts` | `src/services/accounts/` | Users, Instructors |
| `finance` | `src/services/finance/` | Plans, Members, Payments, Expenses, Shifts |
| `dashboard` | `src/services/dashboard/` | Analytics, stats, charts |
| `whisper` | `src/apps/whisper/` | Internal email/notification system |

---

## License

Proprietary — Exarth Corporation. All rights reserved.
