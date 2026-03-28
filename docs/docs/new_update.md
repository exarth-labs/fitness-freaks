# Gym Management System — Update Plan
**Project:** Fitness Freaks (Pakistan Gym Management)
**Date:** 2026-03-28
**Status:** Planning

---

## Overview

This document tracks all planned changes to align the codebase with actual gym management requirements. Each step includes what changes, what it affects, and a verification checklist to confirm it's done correctly.

---

## Step 1 — Remove `management` App

### What
Delete the `src/services/management/` app entirely (Country and State models). It was boilerplate and has no relevance to a single gym in Pakistan.

### Files Affected
- `src/services/management/` — delete entire directory
- `root/settings.py` — remove `ManagementConfig` from `INSTALLED_APPS`
- `root/urls.py` — remove `management/` URL include
- Database — drop `management_country` and `management_state` tables via migration or reset

### Verification Checklist
- [ ] `src/services/management/` directory no longer exists
- [ ] `ManagementConfig` removed from `INSTALLED_APPS` in `settings.py`
- [ ] `management/` URL removed from `root/urls.py`
- [ ] `python manage.py check` passes with 0 issues
- [ ] No broken imports or references to `management` anywhere in codebase

---

## Step 2 — Add `GymShift` Model

### What
Add a `GymShift` model to the `finance` app to represent gender-based timing slots. The gym currently runs:
- Men: 8AM–10AM
- Women: 10AM–2PM
- Men: 2PM–11PM
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

### Files Affected
- `src/services/finance/models.py` — add `GymShift` model
- `src/services/finance/admin.py` — register `GymShiftAdmin`
- `src/services/finance/forms.py` — add `GymShiftForm`
- `src/services/finance/views.py` — add List, Create, Update, Delete views
- `src/services/finance/urls.py` — add shift URL patterns
- `database` — new migration

### New URL Patterns
- `GET  /finance/shifts/` — list shifts
- `POST /finance/shifts/create/` — create shift (AJAX)
- `POST /finance/shifts/update/<pk>/` — update shift (AJAX)
- `POST /finance/shifts/delete/<pk>/` — delete shift

### Seed Data (to be added after migration)
| Name | Gender | Start | End |
|---|---|---|---|
| Morning Men | male | 08:00 | 10:00 |
| Women | female | 10:00 | 14:00 |
| Evening Men | male | 14:00 | 23:00 |

### Verification Checklist
- [ ] `GymShift` model exists and migrated
- [ ] 3 default shifts created (Morning Men, Women, Evening Men)
- [ ] Admin panel shows GymShift with list_display: name, gender, start_time, end_time, is_active
- [ ] CRUD views work (list, create, update, delete)
- [ ] `python manage.py check` passes with 0 issues

---

## Step 3 — Add `Instructor` Model

### What
Add an `Instructor` model to the `accounts` app. Instructors are staff users with an extra profile. Member-to-instructor assignment is future scope — field added now as nullable.

### Model: `Instructor` (in `src/services/accounts/`)
| Field | Type | Notes |
|---|---|---|
| `user` | OneToOneField → User | CASCADE |
| `specialization` | CharField(100) | e.g. "Cardio", "Weight Training", "Boxing" |
| `hire_date` | DateField | default today |
| `bio` | TextField | nullable, blank |
| `is_active` | BooleanField | Default True |
| `created_on` | DateTimeField | auto_now_add |

### Files Affected
- `src/services/accounts/models.py` — add `Instructor` model
- `src/services/accounts/admin.py` — register `InstructorAdmin`
- `src/services/accounts/forms.py` — add `InstructorForm`
- `src/services/accounts/views.py` — add List, Create, Update, Delete, Detail views
- `src/services/accounts/urls.py` — add instructor URL patterns
- `database` — new migration

### New URL Patterns
- `GET  /accounts/instructors/` — list instructors
- `GET  /accounts/instructors/<pk>/` — instructor detail
- `POST /accounts/instructors/create/` — create (AJAX)
- `POST /accounts/instructors/update/<pk>/` — update (AJAX)
- `POST /accounts/instructors/delete/<pk>/` — delete

### Verification Checklist
- [ ] `Instructor` model exists and migrated
- [ ] Instructor must be linked to a User (staff)
- [ ] Admin panel shows Instructor with list_display: user, specialization, hire_date, is_active
- [ ] CRUD views work (list, detail, create, update, delete)
- [ ] `python manage.py check` passes with 0 issues

---

## Step 4 — Update `Member` Model

### What
Add new fields to the existing `Member` model to support gender tracking, shift assignment, instructor assignment, and a direct phone number for quick contact.

### New Fields on `Member`
| Field | Type | Notes |
|---|---|---|
| `gender` | CharField choices | `male` / `female` — required |
| `shift` | ForeignKey → GymShift | SET_NULL, nullable — auto-suggested by gender |
| `instructor` | ForeignKey → Instructor | SET_NULL, nullable — future assignment |
| `phone_number` | CharField(15) | Member's own contact number, nullable |

### Files Affected
- `src/services/finance/models.py` — add fields to `Member`
- `src/services/finance/forms.py` — update `MemberForm` and `MemberQuickAddForm`
- `src/services/finance/admin.py` — update `MemberAdmin` list_display and filters
- `database` — new migration (all new fields nullable/default so no data loss)

### Behaviour Notes
- `gender` is required on create
- `shift` is optional but should be filtered by gender in the form (men see male/both shifts, women see female/both shifts)
- `instructor` is optional (nullable) — shown in form for future use
- `phone_number` is separate from `user.phone_number` — staff can see it without opening user profile

### Verification Checklist
- [ ] `gender` field exists on Member model (male/female choices)
- [ ] `shift` FK to GymShift exists on Member (nullable)
- [ ] `instructor` FK to Instructor exists on Member (nullable)
- [ ] `phone_number` field exists on Member (nullable)
- [ ] `MemberForm` includes all new fields
- [ ] `MemberAdmin` updated to show gender, shift in list_display
- [ ] Migration runs cleanly with no errors
- [ ] `python manage.py check` passes with 0 issues

---

## Step 5 — Update Dashboard: Defaulters Section

### What
Add a **Defaulters** section to the dashboard view that flags members who need attention:
1. Subscription expired (`status = EXPIRED`) — fee not renewed
2. Payment pending/failed — fee not collected

### Changes to `DashboardView`
Add to `get_dashboard_statistics()`:
- `defaulters` — queryset of Members with `status=EXPIRED` or latest Payment `status=PENDING/FAILED`, ordered by `subscription_end` ascending (most overdue first)
- `defaulters_count` — total count for the stats card

### Files Affected
- `src/services/dashboard/views.py` — extend `get_dashboard_statistics()`
- `templates/` dashboard template — add defaulters table/card

### Verification Checklist
- [ ] Dashboard shows a defaulters count card
- [ ] Defaulters list shows: member name, phone, subscription_end, days overdue
- [ ] List is ordered by most overdue first
- [ ] Empty state shows correctly when no defaulters
- [ ] Only visible to staff/admin

---

## Step 6 — Notifications: Email for Expiring Subscriptions + Phone Field

### What
1. Add email trigger when a member's subscription is within 7 days of expiry
2. Phone number is already on Member model (added in Step 4) — SMS implementation deferred to future
3. Whisper (`EmailNotification`) already exists — wire it up for expiry alerts

### Trigger Logic
- Run check daily (via management command or cron)
- For each member where `subscription_end` is between today and today+7 days AND `status=ACTIVE`:
  - If no expiry email sent in last 7 days → create `EmailNotification` record and send

### New Management Command
`python manage.py send_expiry_reminders`
- Located at `src/services/finance/management/commands/send_expiry_reminders.py`
- Can be scheduled via cron on server

### Files Affected
- `src/services/finance/management/commands/send_expiry_reminders.py` — new management command
- `src/apps/whisper/` — use existing `NotificationService` to send

### Verification Checklist
- [ ] Management command exists and runs without error
- [ ] Members expiring in ≤ 7 days receive an email (check Whisper EmailNotification records)
- [ ] Members already expired are NOT emailed (only ACTIVE)
- [ ] Running the command twice does not send duplicate emails
- [ ] `phone_number` field on Member is present (done in Step 4)

---

## Final Verification (Run After All Steps Complete)

- [ ] `python manage.py check` — 0 issues
- [ ] `python manage.py migrate` — all migrations applied cleanly
- [ ] `python manage.py runserver` — server starts without errors
- [ ] Admin panel loads at `/admin/`
- [ ] Dashboard loads at `/dashboard/`
- [ ] Finance: Members, Payments, Expenses, Plans, Shifts all work
- [ ] Accounts: Users, Instructors all work
- [ ] Management app is completely gone (no 404 or import errors)
- [ ] `GET /` redirects to login
- [ ] Login works and redirects correctly to dashboard

---

## Summary Table

| Step | Area | Type | Status |
|---|---|---|---|
| 1 | Remove `management` app | Deletion | Pending |
| 2 | Add `GymShift` model | New model + CRUD | Pending |
| 3 | Add `Instructor` model | New model + CRUD | Pending |
| 4 | Update `Member` model | Model update | Pending |
| 5 | Dashboard defaulters | Feature | Pending |
| 6 | Expiry email notifications | Feature | Pending |
