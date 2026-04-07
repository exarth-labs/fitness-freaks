from django.utils.decorators import method_decorator
from django.views.generic import (
    TemplateView
)
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from datetime import timedelta
from decimal import Decimal
import json

from src.services.accounts.decorators import staff_required_decorator


def get_dashboard_statistics():
    """Calculate all dashboard statistics"""
    from src.services.finance.models import Member, Payment, Expense, SubscriptionPlan, SubscriptionStatus, PaymentStatus

    today = timezone.now().date()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    week_later = today + timedelta(days=7)

    stats = {}

    # Member Statistics
    stats['total_members'] = Member.objects.filter(is_active=True).count()
    stats['active_members'] = Member.objects.filter(status=SubscriptionStatus.ACTIVE, is_active=True).count()
    stats['expired_members'] = Member.objects.filter(status=SubscriptionStatus.EXPIRED, is_active=True).count()
    stats['pending_members'] = Member.objects.filter(status=SubscriptionStatus.PENDING, is_active=True).count()
    stats['new_members_today'] = Member.objects.filter(join_date=today).count()
    stats['new_members_month'] = Member.objects.filter(join_date__gte=month_start).count()

    # Expiring Soon (next 7 days)
    stats['expiring_soon'] = Member.objects.filter(
        subscription_end__gte=today,
        subscription_end__lte=week_later,
        status=SubscriptionStatus.ACTIVE
    ).count()
    stats['expiring_members'] = Member.objects.filter(
        subscription_end__gte=today,
        subscription_end__lte=week_later,
        status=SubscriptionStatus.ACTIVE
    ).select_related('user', 'subscription_plan')[:5]

    # Revenue Statistics (Payments)
    paid_payments = Payment.objects.filter(status=PaymentStatus.PAID)

    stats['revenue_today'] = paid_payments.filter(
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['revenue_month'] = paid_payments.filter(
        payment_date__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['revenue_year'] = paid_payments.filter(
        payment_date__date__gte=year_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['payments_today'] = paid_payments.filter(payment_date__date=today).count()
    stats['payments_month'] = paid_payments.filter(payment_date__date__gte=month_start).count()

    # Expense Statistics
    stats['expenses_today'] = Expense.objects.filter(
        expense_date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['expenses_month'] = Expense.objects.filter(
        expense_date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    stats['expenses_year'] = Expense.objects.filter(
        expense_date__gte=year_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Net Profit
    stats['net_profit_month'] = stats['revenue_month'] - stats['expenses_month']
    stats['net_profit_year'] = stats['revenue_year'] - stats['expenses_year']

    # Recent Payments
    stats['recent_payments'] = Payment.objects.filter(
        status=PaymentStatus.PAID
    ).select_related('member__user', 'subscription_plan').order_by('-payment_date')[:5]

    # Subscription Plan Distribution
    stats['plan_distribution'] = SubscriptionPlan.objects.filter(is_active=True).annotate(
        member_count=Count('members', filter=Q(members__status=SubscriptionStatus.ACTIVE))
    ).values('name', 'member_count').order_by('-member_count')

    # Monthly Revenue Chart Data (last 6 months)
    # Generate last 6 months list
    months_list = []
    for i in range(5, -1, -1):  # 5, 4, 3, 2, 1, 0
        if i == 0:
            month_date = today.replace(day=1)
        else:
            # Calculate months back
            year = today.year
            month = today.month - i
            while month <= 0:
                month += 12
                year -= 1
            month_date = today.replace(year=year, month=month, day=1)
        months_list.append(month_date)

    stats['chart_labels'] = [m.strftime('%b %Y') for m in months_list]

    # Get revenue data
    monthly_revenue = paid_payments.filter(
        payment_date__date__gte=months_list[0]
    ).annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    revenue_dict = {item['month'].replace(day=1): float(item['total']) for item in monthly_revenue}
    stats['chart_revenue'] = [revenue_dict.get(m, 0) for m in months_list]

    # Monthly Expenses Chart Data
    monthly_expenses = Expense.objects.filter(
        expense_date__gte=months_list[0]
    ).annotate(
        month=TruncMonth('expense_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    expenses_dict = {item['month'].replace(day=1): float(item['total']) for item in monthly_expenses}
    stats['chart_expenses'] = [expenses_dict.get(m, 0) for m in months_list]

    # Payment Method Distribution
    stats['payment_methods'] = paid_payments.filter(
        payment_date__date__gte=month_start
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('amount')
    ).order_by('-total')

    # Defaulters — expired members who haven't renewed (most overdue first)
    defaulters_qs = Member.objects.filter(
        status=SubscriptionStatus.EXPIRED,
        is_active=True
    ).select_related('user', 'subscription_plan', 'shift').order_by('subscription_end')

    stats['defaulters'] = defaulters_qs[:20]
    stats['defaulters_count'] = defaulters_qs.count()

    # Monthly new members chart data (last 6 months)
    monthly_new_members = Member.objects.filter(
        join_date__gte=months_list[0]
    ).annotate(
        month=TruncMonth('join_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    new_members_dict = {item['month'].replace(day=1): item['count'] for item in monthly_new_members}
    stats['chart_new_members'] = [new_members_dict.get(m, 0) for m in months_list]

    # Active rate percentage
    stats['active_rate'] = round(
        (stats['active_members'] / stats['total_members'] * 100) if stats['total_members'] > 0 else 0, 1
    )

    return stats


@method_decorator(staff_required_decorator, name='dispatch')
class DashboardView(TemplateView):
    """
    Gym Dashboard with comprehensive statistics
    - Member stats: Total, Active, Expired, Expiring Soon
    - Revenue: Today, Month, Year with charts
    - Expenses tracking and comparison
    - Recent activity feed
    """
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        stats = get_dashboard_statistics()

        # Only set chart data when there's at least one non-zero value
        has_revenue = any(v > 0 for v in stats.get('chart_revenue', []))
        has_expenses = any(v > 0 for v in stats.get('chart_expenses', []))
        has_members_data = any(v > 0 for v in stats.get('chart_new_members', []))

        if has_revenue or has_expenses:
            stats['chart_labels_json'] = json.dumps(stats.get('chart_labels', []))
            stats['chart_revenue_json'] = json.dumps(stats.get('chart_revenue', []))
            stats['chart_expenses_json'] = json.dumps(stats.get('chart_expenses', []))

        if has_members_data:
            stats['chart_new_members_json'] = json.dumps(stats.get('chart_new_members', []))

        context.update(stats)
        return context



