from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import SubscriptionPlan, GymShift, Member, Payment, Expense, PaymentTypeChoice
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML, Field


class GymShiftForm(forms.ModelForm):
    class Meta:
        model = GymShift
        fields = ['name', 'gender', 'start_time', 'end_time', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-time me-1"></i>Shift Details</h6>'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    Column('gender', css_class='form-group col-md-6 mb-0'),
                ),
                Row(
                    Column('start_time', css_class='form-group col-md-4 mb-0'),
                    Column('end_time', css_class='form-group col-md-4 mb-0'),
                    Column('is_active', css_class='form-group col-md-4 mb-0'),
                ),
            ),
        )


class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'name', 'duration_days', 'price', 'description',
            'has_personal_trainer', 'has_locker', 'has_cardio_access', 'has_weight_training',
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-package me-1"></i>Plan Details</h6>'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    Column('duration_days', css_class='form-group col-md-3 mb-0'),
                    Column('price', css_class='form-group col-md-3 mb-0'),
                ),
                Row(
                    Column('is_active', css_class='form-group col-md-3 mb-0'),
                    Column('has_personal_trainer', css_class='form-group col-md-3 mb-0'),
                    Column('has_locker', css_class='form-group col-md-3 mb-0'),
                    Column('has_cardio_access', css_class='form-group col-md-3 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-list-ul me-1"></i>Description</h6>'),
                'description',
            ),
        )


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'user', 'shift', 'instructor',
            'subscription_plan', 'subscription_start', 'subscription_end', 'status',
            'emergency_contact_name', 'emergency_contact_phone',
            'blood_group', 'health_conditions', 'weight', 'height',
            'join_date', 'notes', 'is_active'
        ]
        widgets = {
            'health_conditions': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any medical conditions, allergies, etc.'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes about this member'}),
            'subscription_start': forms.DateInput(attrs={'type': 'date'}),
            'subscription_end': forms.DateInput(attrs={'type': 'date'}),
            'join_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].help_text = "Inactive members cannot access gym services and are excluded from reports"
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            # Assignment section
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-user me-1"></i>Assignment</h6>'),
                Row(
                    Column('user', css_class='form-group col-md-4 mb-0'),
                    Column('shift', css_class='form-group col-md-4 mb-0'),
                    Column('instructor', css_class='form-group col-md-4 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
            # Subscription section
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-id-card me-1"></i>Subscription</h6>'),
                Row(
                    Column('subscription_plan', css_class='form-group col-md-4 mb-0'),
                    Column('subscription_start', css_class='form-group col-md-4 mb-0'),
                    Column('subscription_end', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('join_date', css_class='form-group col-md-4 mb-0'),
                    Column('status', css_class='form-group col-md-4 mb-0'),
                    Column('is_active', css_class='form-group col-md-4 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
            # Emergency contact section
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-phone-call me-1"></i>Emergency Contact</h6>'),
                Row(
                    Column('emergency_contact_name', css_class='form-group col-md-6 mb-0'),
                    Column('emergency_contact_phone', css_class='form-group col-md-6 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
            # Health section
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-heart me-1"></i>Health Information</h6>'),
                Row(
                    Column('blood_group', css_class='form-group col-md-4 mb-0'),
                    Column('weight', css_class='form-group col-md-4 mb-0'),
                    Column('height', css_class='form-group col-md-4 mb-0'),
                ),
                'health_conditions',
                HTML('<hr class="my-4">'),
            ),
            # Notes section
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-note me-1"></i>Notes</h6>'),
                'notes',
            ),
        )


class MemberQuickAddForm(forms.ModelForm):
    """Simplified form for quick member registration"""
    class Meta:
        model = Member
        fields = [
            'user', 'shift',
            'subscription_plan',
            'emergency_contact_name', 'emergency_contact_phone',
            'blood_group', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('user', css_class='form-group col-md-6 mb-0'),
                Column('shift', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('subscription_plan', css_class='form-group col-md-6 mb-0'),
                Column('blood_group', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('emergency_contact_name', css_class='form-group col-md-6 mb-0'),
                Column('emergency_contact_phone', css_class='form-group col-md-6 mb-0'),
            ),
            'notes',
        )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'member', 'subscription_plan', 'payment_type', 'amount', 'registration_fee', 'discount',
            'payment_method', 'payment_date', 'reference_number',
            'status', 'period_start', 'period_end', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Payment notes...'}),
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['registration_fee'].help_text = "Auto-filled based on payment type"
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-user me-1"></i>Payment Details</h6>'),
                Row(
                    Column('member', css_class='form-group col-md-6 mb-0'),
                    Column('subscription_plan', css_class='form-group col-md-6 mb-0'),
                ),
                Row(
                    Column('payment_type', css_class='form-group col-md-4 mb-0'),
                    Column('amount', css_class='form-group col-md-4 mb-0'),
                    Column('discount', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('registration_fee', css_class='form-group col-md-4 mb-0'),
                    Column('payment_method', css_class='form-group col-md-4 mb-0'),
                    Column('reference_number', css_class='form-group col-md-4 mb-0'),
                ),
                HTML('<div class="mb-3"><small class="text-muted"><strong>Total:</strong> PKR <span id="total-amount">0</span></small></div>'),
                Row(
                    Column('status', css_class='form-group col-md-4 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-calendar me-1"></i>Period & Notes</h6>'),
                Row(
                    Column('payment_date', css_class='form-group col-md-4 mb-0'),
                    Column('period_start', css_class='form-group col-md-4 mb-0'),
                    Column('period_end', css_class='form-group col-md-4 mb-0'),
                ),
                'notes',
            ),
        )


class QuickPaymentForm(forms.ModelForm):
    """Simplified payment form for quick fee collection"""
    class Meta:
        model = Payment
        fields = ['member', 'subscription_plan', 'payment_type', 'amount', 'registration_fee', 'discount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['registration_fee'].help_text = "Auto-filled based on payment type"
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('member', css_class='form-group col-md-6 mb-0'),
                Column('subscription_plan', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('payment_type', css_class='form-group col-md-4 mb-0'),
                Column('amount', css_class='form-group col-md-4 mb-0'),
                Column('discount', css_class='form-group col-md-4 mb-0'),
            ),
            Row(
                Column('registration_fee', css_class='form-group col-md-4 mb-0'),
                Column('payment_method', css_class='form-group col-md-4 mb-0'),
                Column('reference_number', css_class='form-group col-md-4 mb-0'),
            ),
            'notes',
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.subscription_plan:
            instance.period_start = timezone.now().date()
            instance.period_end = instance.period_start + timedelta(days=instance.subscription_plan.duration_days)
        if commit:
            instance.save()
        return instance


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'category', 'amount', 'description', 'expense_date',
            'payment_method', 'reference_number', 'is_recurring'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Expense description...'}),
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-receipt me-1"></i>Expense Details</h6>'),
                Row(
                    Column('category', css_class='form-group col-md-4 mb-0'),
                    Column('amount', css_class='form-group col-md-4 mb-0'),
                    Column('expense_date', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('payment_method', css_class='form-group col-md-4 mb-0'),
                    Column('reference_number', css_class='form-group col-md-4 mb-0'),
                    Column('is_recurring', css_class='form-group col-md-4 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-list-ul me-1"></i>Description</h6>'),
                'description',
            ),
        )


class RenewSubscriptionForm(forms.Form):
    """Form for renewing member subscription"""
    subscription_plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        label='Subscription Plan'
    )
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Amount (PKR)')
    discount = forms.DecimalField(
        max_digits=10, decimal_places=2, initial=0, required=False, label='Discount (PKR)'
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Cash'),
            ('jazzcash', 'JazzCash'),
            ('easypaisa', 'Easypaisa'),
            ('bank_transfer', 'Bank Transfer'),
            ('card', 'Debit/Credit Card'),
        ],
        initial='cash'
    )
    reference_number = forms.CharField(max_length=100, required=False, label='Reference/Receipt No.')
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

