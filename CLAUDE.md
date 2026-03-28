# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Fitness Freaks** is a Django-based gym management system for tracking members, subscriptions, payments, and expenses. It uses server-side rendered templates with Bootstrap 5 — there is no frontend build step.

## Commands

### Setup
```bash
# Automated setup (creates venv, installs deps, runs migrations, creates superuser)
chmod +x docs/bash/setup.sh && ./docs/bash/setup.sh

# Manual
python -m venv venv && source venv/bin/activate
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
./docs/bash/faker.sh                # Seed database with fake data
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
  core/         # Shared mixins, utilities, base models, template tags
  services/
    accounts/   # Custom User model (email-based), user CRUD, permissions
    dashboard/  # Analytics: member stats, revenue charts, expiring subs
    finance/    # SubscriptionPlan, Member, Payment, Expense models
    management/ # Country/State geographic models
  apps/
    whisper/    # Internal notification/email system
  website/      # Public-facing pages
templates/      # HTML templates (base, account, socialaccount layouts)
static/         # CSS, JS, images
docs/bash/      # Utility shell scripts
```

### Core Patterns

**Reusable CRUD Mixins** (`src/core/`): All service apps inherit from `CoreListViewMixin`, `CoreDetailViewMixin`, `CoreCreateViewMixin`, `CoreUpdateViewMixin`, `CoreDeleteViewMixin` for consistent CRUD behavior.

**Dynamic Forms**: `get_dynamic_crispy_form()` generates Crispy Bootstrap 5 forms at runtime.

**URL Helpers**: `get_action_urls()` provides standardized action URL resolution across apps.

**Custom Permissions**: Permission checks are handled via middleware and decorators in `src/core/`, not Django's built-in permission framework.

### Domain Models (Finance App)

- `SubscriptionPlan` — gym membership tiers
- `Member` — gym members (health info, CNIC, emergency contacts, linked User)
- `Payment` — tracks cash/JazzCash/Easypaisa/bank/card transactions; statuses: paid/pending/failed/refunded
- `Expense` — rent/utilities/salaries/equipment/marketing categories

### Authentication

- Email-based login via `django-allauth` (username login disabled)
- Google social login enabled
- MFA/FIDO2 support available
- REST API auth via `dj-rest-auth` + JWT
- Two user types: `administration`, `client`

### Settings & Environment

`root/settings.py` uses `django-environ` to read from `.env`:
- `ENVIRONMENT=local` → SQLite; `ENVIRONMENT=server` → PostgreSQL
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `TIME_ZONE`
- `EMAIL_HOST`/`EMAIL_PORT`/`EMAIL_HOST_USER` for SMTP
- `MAILCHIMP_API_KEY`, `MAILCHIMP_FROM_EMAIL` for transactional email
