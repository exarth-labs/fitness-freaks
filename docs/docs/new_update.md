# Gym Management System — Update Plan
**Project:** Fitness Freaks (Pakistan Gym Management)
**Date:** 2026-03-28
**Status:** Completed

---

## Overview

This document tracked all planned changes to align the codebase with actual gym management requirements. All 6 steps have been completed and verified.

---

## Step 1 — Remove `management` App ✅

### What
Deleted the `src/services/management/` app entirely (Country and State models). It was boilerplate with no relevance to a single gym in Pakistan.

### Files Changed
- `src/services/management/` — deleted
- `root/settings.py` — removed `ManagementConfig` from `INSTALLED_APPS`
- `root/urls.py` — removed `management/` URL include
- `root/model_lookup.py` — removed Country/State imports

### Verification Checklist
- [x] `src/services/management/` directory no longer exists
- [x] `ManagementConfig` removed from `INSTALLED_APPS` in `settings.py`
- [x] `management/` URL removed from `root/urls.py`
- [x] `python manage.py check` passes with 0 issues
- [x] No broken imports or references to `management` anywhere in codebase

---

## Step 2 — Add `GymShift` Model ✅

### What
Added a `GymShift` model to the `finance` app to represent gender-based timing slots.

### Gym Timings
- Men: 8AM–10AM (Morning Men)
- Women: 10AM–2PM (Women)
- Men: 2PM–11PM (Evening Men)
- Closed: 11PM–8AM

### Model: `GymShift` (in `src/services/finance/`)
| Field | Type | Notes |
|---|---|---|
| `name` | CharField(100) | e.g. "Morning Men", "Women", "Evening Men" |
| `gender` | CharField choices | `male` / `female` / `both` |
| `start_time` | TimeField | Shift start |
| `end_time` | TimeField | Shift end |
| `is_active` | BooleanField | Default True |
| `created_on` | DateTimeField | auto_now_add |

### Files Changed
- `src/services/finance/models.py` — added `GymShift` model
- `src/services/finance/admin.py` — registered `GymShiftAdmin`
- `src/services/finance/forms.py` — added `GymShiftForm`
- `src/services/finance/views.py` — added List, Create, Update, Delete views
- `src/services/finance/urls.py` — added shift URL patterns
- Migration: `finance/0002_gymshift_member_gender_member_instructor_and_more.py`

### URL Patterns
- `GET  /finance/shifts/` — list shifts
- `POST /finance/shifts/create/` — create shift (AJAX)
- `POST /finance/shifts/update/<pk>/` — update shift (AJAX)
- `POST /finance/shifts/delete/<pk>/` — delete shift

### Seed Data Created
| Name | Gender | Start | End |
|---|---|---|---|
| Morning Men | male | 08:00 | 10:00 |
| Women | female | 10:00 | 14:00 |
| Evening Men | male | 14:00 | 23:00 |

### Verification Checklist
- [x] `GymShift` model exists and migrated
- [x] 3 default shifts seeded
- [x] Admin panel shows GymShift with list_display: name, gender, start_time, end_time, is_active
- [x] CRUD views wired up
- [x] `python manage.py check` passes with 0 issues

---

## Step 3 — Add `Instructor` Model ✅

### What
Added an `Instructor` model to the `accounts` app. Instructors are staff users with an extra profile. Member-to-instructor assignment UI is deferred — the FK is already on Member.

### Model: `Instructor` (in `src/services/accounts/`)
| Field | Type | Notes |
|---|---|---|
| `user` | OneToOneField → User | CASCADE |
| `specialization` | CharField(100) | e.g. "Cardio", "Weight Training", "Boxing" |
| `hire_date` | DateField | nullable |
| `bio` | TextField | nullable |
| `is_active` | BooleanField | Default True |
| `created_on` | DateTimeField | auto_now_add |

### Files Changed
- `src/services/accounts/models.py` — added `Instructor` model
- `src/services/accounts/admin.py` — registered `InstructorAdmin`, updated site header to "Fitness Freaks Administration"
- `src/services/accounts/forms.py` — added `InstructorForm`
- `src/services/accounts/views.py` — added List, Create, Update, Delete, Detail views
- `src/services/accounts/urls.py` — added instructor URL patterns
- Migration: `accounts/0002_instructor.py`

### URL Patterns
- `GET  /accounts/instructors/` — list instructors
- `GET  /accounts/instructors/<pk>/` — instructor detail
- `POST /accounts/instructors/create/` — create
- `POST /accounts/instructors/<pk>/update/` — update
- `POST /accounts/instructors/<pk>/delete/` — delete

### Verification Checklist
- [x] `Instructor` model exists and migrated
- [x] Linked to User via OneToOne
- [x] Admin panel shows Instructor with list_display: user, specialization, hire_date, is_active
- [x] CRUD views wired up
- [x] `python manage.py check` passes with 0 issues

---

## Step 4 — Update `Member` Model ✅

### What
Added new fields to the existing `Member` model for gender, shift, instructor assignment, and direct phone contact.

### New Fields on `Member`
| Field | Type | Notes |
|---|---|---|
| `gender` | CharField choices | `male` / `female` — default `male` |
| `shift` | ForeignKey → GymShift | SET_NULL, nullable |
| `instructor` | ForeignKey → Instructor | SET_NULL, nullable — future UI |
| `phone_number` | CharField(15) | Member's own contact number, nullable |

### Files Changed
- `src/services/finance/models.py` — added 4 fields to `Member`
- `src/services/finance/forms.py` — updated `MemberForm` and `MemberQuickAddForm`
- `src/services/finance/admin.py` — updated `MemberAdmin` (list_display, filters, search)
- Migration: included in `finance/0002_gymshift_member_gender_member_instructor_and_more.py`

### Verification Checklist
- [x] `gender`, `shift`, `instructor`, `phone_number` fields exist on Member
- [x] `MemberForm` and `MemberQuickAddForm` include new fields
- [x] `MemberAdmin` shows gender and shift in list_display
- [x] Migration applied cleanly
- [x] `python manage.py check` passes with 0 issues

---

## Step 5 — Dashboard: Defaulters Section ✅

### What
Added a Defaulters section to the dashboard — members whose subscription has expired and not been renewed, ordered most overdue first.

### Changes Made
- `get_dashboard_statistics()` now returns:
  - `defaulters` — up to 20 expired active members, ordered by `subscription_end` asc
  - `defaulters_count` — total count
- Dashboard template updated with:
  - Red stat card showing defaulters count
  - Full defaulters table: name, phone, plan, shift, expiry date, days overdue, Renew button
  - Empty state message when no defaulters

### Files Changed
- `src/services/dashboard/views.py` — extended `get_dashboard_statistics()`
- `src/services/dashboard/templates/dashboard/dashboard.html` — added stat card + table

### Verification Checklist
- [x] Dashboard shows a defaulters count stat card (red)
- [x] Defaulters table shows: name, phone, plan, shift, expiry date, days overdue
- [x] Ordered most overdue first
- [x] Empty state renders correctly
- [x] Only visible to staff/admin (protected by `staff_required_decorator`)

---

## Step 6 — Expiry Email Notifications ✅

### What
Added a daily management command that emails members whose subscription expires within 7 days. Duplicate sending is prevented. SMS deferred to future (phone field is in place).

### Trigger Logic
- Targets members with `status=ACTIVE` and `subscription_end` between today and today+7
- Skips if a reminder email was already sent within the last 7 days (checks `EmailNotification` records)
- Uses existing `NotificationService.send_email_notification_smtp()`

### Files Created
- `src/services/finance/management/commands/send_expiry_reminders.py` — management command
- `src/apps/whisper/templates/whisper/email/expiry_reminder.html` — email template

### Usage
```bash
python manage.py send_expiry_reminders
```

### Cron (server)
```
0 9 * * * python manage.py send_expiry_reminders
```

### Verification Checklist
- [x] Management command discovered and runs without error
- [x] Only emails ACTIVE members expiring in ≤ 7 days
- [x] Duplicate prevention via `EmailNotification` record check
- [x] Email template extends whisper base layout
- [x] `phone_number` field on Member is present (Step 4)

---

## Final Verification ✅

- [x] `python manage.py check` — 0 issues
- [x] All migrations applied cleanly
- [x] No references to `management` or `website` apps remain
- [x] `GET /` redirects to login
- [x] Finance: Members, Payments, Expenses, Plans, Shifts — all wired
- [x] Accounts: Users, Instructors — all wired
- [x] Dashboard: stats, charts, expiring soon, defaulters — all present

---

## Deferred (Future Work)

| Item | Notes |
|---|---|
| Instructor → Member assignment UI | FK is on Member, just needs a form widget |
| SMS notifications | `phone_number` field exists on Member, implementation later |
| Member-facing dashboard | Login works, dashboard UI not built yet |

---

---

## Step 7 — Django 5.2 + allauth 65.x Upgrade ✅

### What
Upgraded from Django 3.x + allauth 0.55.x to Django 5.2.12 + allauth 65.15.0. Required several breaking-change fixes.

### Django 5.x Breaking Changes Applied

| Setting / Change | Action |
|---|---|
| `USE_L10N` removed in Django 5.0 | Deleted from `settings.py` (localization is always on now) |
| `import datetime` in settings | Removed — was unused |

### allauth 65.x Breaking Changes Applied

| Old Setting | New Setting | Notes |
|---|---|---|
| `ACCOUNT_EMAIL_REQUIRED = True` | `ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']` | Deprecated in 65.x |
| `ACCOUNT_USERNAME_REQUIRED = False` | Removed | Covered by `ACCOUNT_SIGNUP_FIELDS` |
| `ACCOUNT_ALLOW_REGISTRATION = False` | `ACCOUNT_SIGNUP_ENABLED = False` | Deprecated in 65.x |
| `ACCOUNT_LOGIN_METHODS = ['email']` | `ACCOUNT_LOGIN_METHODS = {'email'}` | Must be a set, not a list |
| `allauth.account.middleware.AccountMiddleware` commented out | Uncommented — now **required** by allauth 65.x | Server won't start without it |

### Template Fixes
Removed `{% load socialaccount %}` and `{% load account socialaccount %}` from all account templates after `allauth.socialaccount` was dropped from `INSTALLED_APPS`:
- `templates/account/login.html`
- `templates/account/logout.html`
- `templates/account/email_confirm.html`
- `templates/account/password_reset_done.html`
- `templates/account/verification_sent.html`
- `templates/account/signup.html`
- `templates/account/complete_profile_vendor.html`

### allauth Social Auth Removed
- Removed `allauth.socialaccount` + `allauth.socialaccount.providers.google` from `INSTALLED_APPS`
- Removed `GOOGLE_CALLBACK_ADDRESS`, `APPLE_CALLBACK_ADDRESS`, `SOCIALACCOUNT_EMAIL_VERIFICATION` from settings
- Updated `root/urls.py`: `include('allauth.urls')` → `include('allauth.account.urls')` (drops all social endpoints)
- Added signup URL redirect: `path('accounts/signup/', RedirectView.as_view(url='/accounts/login/'))`

### Verification Checklist
- [x] `python manage.py check` — 0 issues, 0 warnings
- [x] `GET /accounts/login/` returns 200
- [x] `GET /` redirects to login (302 → 200)
- [x] No `socialaccount` template tag errors
- [x] All deprecated settings replaced

---

## Summary Table

| Step | Area | Type | Status |
|---|---|---|---|
| 1 | Remove `management` app | Deletion | Done |
| 2 | Add `GymShift` model | New model + CRUD | Done |
| 3 | Add `Instructor` model | New model + CRUD | Done |
| 4 | Update `Member` model | Model update | Done |
| 5 | Dashboard defaulters | Feature | Done |
| 6 | Expiry email notifications | Feature | Done |
| 7 | Django 5.2 + allauth 65.x upgrade | Compatibility | Done |
