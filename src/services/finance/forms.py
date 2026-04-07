from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import SubscriptionPlan, GymShift, Member, Payment, Expense
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
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            # Assignment section
            Div(
                HTML('<h5 class="mb-3"><i class="bx bx-user me-1"></i>Assignment</h5>'),
                Row(
                    Column('user', css_class='form-group col-md-6 mb-0'),
                    Column('shift', css_class='form-group col-md-6 mb-0'),
                ),
                Row(
                    Column('instructor', css_class='form-group col-md-6 mb-0'),
                ),
                css_class='mb-4',
            ),
            # Subscription section
            Div(
                HTML('<h5 class="mb-3"><i class="bx bx-id-card me-1"></i>Subscription</h5>'),
                Row(
                    Column('subscription_plan', css_class='form-group col-md-4 mb-0'),
                    Column('subscription_start', css_class='form-group col-md-4 mb-0'),
                    Column('subscription_end', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('status', css_class='form-group col-md-4 mb-0'),
                    Column('is_active', css_class='form-group col-md-4 mb-0'),
                    Column('join_date', css_class='form-group col-md-4 mb-0'),
                ),
                css_class='mb-4',
            ),
            # Emergency contact section
            Div(
                HTML('<h5 class="mb-3"><i class="bx bx-phone-call me-1"></i>Emergency Contact</h5>'),
                Row(
                    Column('emergency_contact_name', css_class='form-group col-md-6 mb-0'),
                    Column('emergency_contact_phone', css_class='form-group col-md-6 mb-0'),
                ),
                css_class='mb-4',
            ),
            # Health section
            Div(
                HTML('<h5 class="mb-3"><i class="bx bx-heart me-1"></i>Health Information</h5>'),
                Row(
                    Column('blood_group', css_class='form-group col-md-3 mb-0'),
                    Column('weight', css_class='form-group col-md-3 mb-0'),
                    Column('height', css_class='form-group col-md-3 mb-0'),
                ),
                'health_conditions',
                css_class='mb-4',
            ),
            # Notes section
            Div(
                HTML('<h5 class="mb-3"><i class="bx bx-note me-1"></i>Notes</h5>'),
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
            'member', 'subscription_plan', 'amount', 'discount',
            'payment_method', 'payment_date', 'reference_number',
            'status', 'period_start', 'period_end', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-populate amount when subscription plan changes
        if 'subscription_plan' in self.data:
            try:
                plan_id = int(self.data.get('subscription_plan'))
                plan = SubscriptionPlan.objects.get(pk=plan_id)
                self.fields['amount'].initial = plan.price
            except (ValueError, SubscriptionPlan.DoesNotExist):
                pass


class QuickPaymentForm(forms.ModelForm):
    """Simplified payment form for quick fee collection"""
    class Meta:
        model = Payment
        fields = ['member', 'subscription_plan', 'amount', 'discount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

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
            'description': forms.Textarea(attrs={'rows': 3}),
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
        }


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

