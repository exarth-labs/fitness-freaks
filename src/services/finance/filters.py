import django_filters
from django import forms
from django.db import models

from .models import (
    SubscriptionPlan, Member, Payment, Expense,
    SubscriptionStatus, PaymentStatus, PaymentMethodChoice, ExpenseCategory
)



def filter_boolean(queryset, name, value):
    if value == 'true':
        return queryset.filter(**{name: True})
    elif value == 'false':
        return queryset.filter(**{name: False})
    return queryset


class SubscriptionPlanFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Plan Name',
        widget=forms.TextInput(attrs={'placeholder': 'Search by name...'}),
    )
    min_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte', label='Min Price',
        widget=forms.NumberInput(attrs={'placeholder': 'Min PKR'}),
    )
    max_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte', label='Max Price',
        widget=forms.NumberInput(attrs={'placeholder': 'Max PKR'}),
    )
    is_active = django_filters.ChoiceFilter(
        choices=[('', 'All Plans'), ('true', 'Active'), ('false', 'Inactive')],
        empty_label=None,
        label='Plan Status',
        method='filter_is_active',
    )
    has_personal_trainer = django_filters.ChoiceFilter(
        choices=[('', 'Trainer: Any'), ('true', 'With Trainer'), ('false', 'No Trainer')],
        empty_label=None,
        label='Personal Trainer',
        method='filter_has_personal_trainer',
    )
    has_locker = django_filters.ChoiceFilter(
        choices=[('', 'Locker: Any'), ('true', 'With Locker'), ('false', 'No Locker')],
        empty_label=None,
        label='Locker',
        method='filter_has_locker',
    )

    class Meta:
        model = SubscriptionPlan
        fields = []

    def filter_is_active(self, queryset, name, value):
        return filter_boolean(queryset, 'is_active', value)

    def filter_has_personal_trainer(self, queryset, name, value):
        return filter_boolean(queryset, 'has_personal_trainer', value)

    def filter_has_locker(self, queryset, name, value):
        return filter_boolean(queryset, 'has_locker', value)


class MemberFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Name, email, CNIC, phone...'}),
    )
    status = django_filters.ChoiceFilter(
        choices=[('', 'All Statuses')] + list(SubscriptionStatus.choices),
        empty_label=None,
        label='Status',
    )
    gender = django_filters.ChoiceFilter(
        choices=[('', 'All Genders'), ('male', 'Male'), ('female', 'Female')],
        empty_label=None,
        label='Gender',
    )
    subscription_plan = django_filters.ModelChoiceFilter(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        empty_label='All Plans',
        label='Plan',
    )
    is_active = django_filters.ChoiceFilter(
        choices=[('', 'All Members'), ('true', 'Active Members'), ('false', 'Inactive Members')],
        empty_label=None,
        label='Member Status',
        method='filter_is_active',
    )
    expiring_soon = django_filters.ChoiceFilter(
        choices=[('', 'Expiry: All'), ('true', 'Expiring in 7 Days')],
        empty_label=None,
        label='Expiring',
        method='filter_expiring_soon',
    )

    class Meta:
        model = Member
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(user__email__icontains=value) |
            models.Q(user__first_name__icontains=value) |
            models.Q(user__last_name__icontains=value) |
            models.Q(cnic__icontains=value) |
            models.Q(phone_number__icontains=value) |
            models.Q(emergency_contact_phone__icontains=value)
        )

    def filter_is_active(self, queryset, name, value):
        return filter_boolean(queryset, 'is_active', value)

    def filter_expiring_soon(self, queryset, name, value):
        if value == 'true':
            from django.utils import timezone
            from datetime import timedelta
            today = timezone.now().date()
            week_later = today + timedelta(days=7)
            return queryset.filter(
                subscription_end__gte=today,
                subscription_end__lte=week_later,
                status=SubscriptionStatus.ACTIVE
            )
        return queryset


class PaymentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Member name, reference no...'}),
    )
    status = django_filters.ChoiceFilter(
        choices=[('', 'All Statuses')] + list(PaymentStatus.choices),
        empty_label=None,
        label='Status',
    )
    payment_method = django_filters.ChoiceFilter(
        choices=[('', 'All Methods')] + list(PaymentMethodChoice.choices),
        empty_label=None,
        label='Method',
    )
    date_from = django_filters.DateFilter(
        field_name='payment_date', lookup_expr='gte', label='From Date',
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'From date'}),
    )
    date_to = django_filters.DateFilter(
        field_name='payment_date', lookup_expr='lte', label='To Date',
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'To date'}),
    )
    min_amount = django_filters.NumberFilter(
        field_name='amount', lookup_expr='gte', label='Min Amount',
        widget=forms.NumberInput(attrs={'placeholder': 'Min PKR'}),
    )
    max_amount = django_filters.NumberFilter(
        field_name='amount', lookup_expr='lte', label='Max Amount',
        widget=forms.NumberInput(attrs={'placeholder': 'Max PKR'}),
    )

    class Meta:
        model = Payment
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(member__user__email__icontains=value) |
            models.Q(member__user__first_name__icontains=value) |
            models.Q(member__user__last_name__icontains=value) |
            models.Q(reference_number__icontains=value)
        )


class ExpenseFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(
        choices=[('', 'All Categories')] + list(ExpenseCategory.choices),
        empty_label=None,
        label='Category',
    )
    payment_method = django_filters.ChoiceFilter(
        choices=[('', 'All Methods')] + list(PaymentMethodChoice.choices),
        empty_label=None,
        label='Method',
    )
    date_from = django_filters.DateFilter(
        field_name='expense_date', lookup_expr='gte', label='From Date',
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'From date'}),
    )
    date_to = django_filters.DateFilter(
        field_name='expense_date', lookup_expr='lte', label='To Date',
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'To date'}),
    )
    min_amount = django_filters.NumberFilter(
        field_name='amount', lookup_expr='gte', label='Min Amount',
        widget=forms.NumberInput(attrs={'placeholder': 'Min PKR'}),
    )
    max_amount = django_filters.NumberFilter(
        field_name='amount', lookup_expr='lte', label='Max Amount',
        widget=forms.NumberInput(attrs={'placeholder': 'Max PKR'}),
    )
    is_recurring = django_filters.ChoiceFilter(
        choices=[('', 'All Expenses'), ('true', 'Recurring'), ('false', 'One-time')],
        empty_label=None,
        label='Recurring',
        method='filter_is_recurring',
    )

    class Meta:
        model = Expense
        fields = []

    def filter_is_recurring(self, queryset, name, value):
        return filter_boolean(queryset, 'is_recurring', value)
