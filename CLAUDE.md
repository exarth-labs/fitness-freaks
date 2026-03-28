# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Fitness Freaks** is a Django-based gym management system for tracking members, subscriptions, payments, and expenses. It uses server-side rendered templates with Bootstrap 5 — there is no frontend build step.

## Commands

### Setup
```bash
# Automated setup (creates .venv, installs deps, runs migrations, creates superuser)
chmod +x docs/bash/setup.sh && ./docs/bash/setup.sh

# Manual
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

### Development
```bash
python manage.py runserver          # Start dev server at localhost:8000
python manage.py shell              # Django shell
```

### Database
```bash
python manage.py makemigrations     # Create new migrations
python manage.py migrate            # Apply migrations
./docs/bash/migrations_clean.sh     # Clean all migration files (use carefully)
```

### Seed & Clean Data
```bash
python manage.py adddata                          # Seed fake data (50 members, 120 payments, 60 expenses, 5 instructors)
python manage.py adddata --members 100 --payments 200 --expenses 80 --instructors 8
python manage.py cleandata --yes                  # Delete all data, keep first superuser
python manage.py cleandata --yes --all            # Also wipe shifts and plans
```

### Notifications
```bash
python manage.py send_expiry_reminders            # Email members expiring within 7 days
```

### Static & Admin
```bash
python manage.py collectstatic
python manage.py createsuperuser    # Or: ./docs/bash/superuser.sh
```

Default dev login: `mark@exarth.com` / `mark` — admin at `/admin/`

## Architecture

### App Layout

```
root/           # Django project config (settings, root URLs, wsgi/asgi)
src/
  core/         # Shared mixins, utilities, base models, template tags, management commands
  services/
    accounts/   # Custom User model (email-based), Instructor model, user CRUD
    dashboard/  # Analytics: member stats, revenue charts, expiring subs, defaulters
    finance/    # SubscriptionPlan, GymShift, Member, Payment, Expense models
  apps/
    whisper/    # Internal notification/email system
templates/      # HTML templates (base, account layouts)
static/         # CSS, JS, images
docs/bash/      # Utility shell scripts
```

### Core Patterns

**Reusable CRUD Mixins** (`src/core/`): All service apps inherit from `CoreListViewMixin`, `CoreDetailViewMixin`, `CoreCreateViewMixin`, `CoreUpdateViewMixin`, `CoreDeleteViewMixin` for consistent CRUD behavior.

**Dynamic Forms**: `get_dynamic_crispy_form()` generates Crispy Bootstrap 5 forms at runtime.

**URL Helpers**: `get_action_urls()` provides standardized action URL resolution across apps.

**Custom Permissions**: Permission checks are handled via middleware and decorators in `src/core/`, not Django's built-in permission framework.

### Domain Models (Finance App)

- `GymShift` — gender-based timing slots (Morning Men, Women, Evening Men)
- `SubscriptionPlan` — gym membership tiers with pricing
- `Member` — gym members (gender, shift, instructor FK, CNIC, health info, emergency contacts, linked User)
- `Payment` — tracks cash/JazzCash/Easypaisa/bank/card transactions; statuses: paid/pending/failed/refunded
- `Expense` — rent/utilities/salaries/equipment/marketing categories

### Domain Models (Accounts App)

- `User` — email-based custom user, types: `administration` / `client`
- `Instructor` — staff profile (specialization, hire date, bio), OneToOne → User

### Authentication

- Email-based login only via `django-allauth` 65.x
- No social login, no signup (registration disabled via `ACCOUNT_SIGNUP_ENABLED = False`)
- `allauth.account.middleware.AccountMiddleware` required in MIDDLEWARE
- Two user types: `administration`, `client`

### Settings & Environment

`root/settings.py` uses `django-environ` to read from `.env`:
- `ENVIRONMENT=local` → SQLite; `ENVIRONMENT=server` → PostgreSQL
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `TIME_ZONE`
- `EMAIL_HOST`/`EMAIL_PORT`/`EMAIL_HOST_USER` for SMTP
- `MAILCHIMP_API_KEY`, `MAILCHIMP_FROM_EMAIL` for transactional email
