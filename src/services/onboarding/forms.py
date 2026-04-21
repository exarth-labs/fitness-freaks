from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML

from src.services.finance.models import Member, Payment, SubscriptionPlan


class WizardMemberForm(forms.ModelForm):
    """MemberForm for the wizard — user field excluded, set in done()."""

    class Meta:
        model = Member
        fields = [
            'shift', 'instructor',
            'subscription_plan', 'subscription_start', 'subscription_end', 'status',
            'emergency_contact_name', 'emergency_contact_phone',
            'blood_group', 'health_conditions', 'weight', 'height',
            'join_date', 'notes', 'is_active',
        ]
        widgets = {
            'health_conditions': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'subscription_start': forms.DateInput(attrs={'type': 'date'}),
            'subscription_end': forms.DateInput(attrs={'type': 'date'}),
            'join_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-time me-1"></i>Shift & Trainer</h6>'),
                Row(
                    Column('shift', css_class='form-group col-md-6 mb-0'),
                    Column('instructor', css_class='form-group col-md-6 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
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
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-phone-call me-1"></i>Emergency Contact</h6>'),
                Row(
                    Column('emergency_contact_name', css_class='form-group col-md-6 mb-0'),
                    Column('emergency_contact_phone', css_class='form-group col-md-6 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
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
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-note me-1"></i>Notes</h6>'),
                'notes',
            ),
        )


class WizardPaymentForm(forms.ModelForm):
    """PaymentForm for the wizard — member field excluded, set in done()."""

    class Meta:
        model = Payment
        fields = [
            'subscription_plan', 'payment_type', 'amount', 'registration_fee', 'discount',
            'payment_method', 'payment_date', 'reference_number',
            'status', 'period_start', 'period_end', 'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'payment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        import json
        super().__init__(*args, **kwargs)
        self.fields['registration_fee'].help_text = "Auto-filled based on payment type"
        self.fields['registration_fee'].widget.attrs['id'] = 'id_registration_fee'

        plan_prices = {str(p.pk): str(p.price) for p in SubscriptionPlan.objects.all()}
        self.fields['subscription_plan'].widget.attrs['data-plans'] = json.dumps(plan_prices)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-receipt me-1"></i>Payment Details</h6>'),
                Row(
                    Column('subscription_plan', css_class='form-group col-md-4 mb-0'),
                    Column('payment_type', css_class='form-group col-md-4 mb-0'),
                    Column('status', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('amount', css_class='form-group col-md-4 mb-0'),
                    Column('discount', css_class='form-group col-md-4 mb-0'),
                    Column('registration_fee', css_class='form-group col-md-4 mb-0 reg-fee-col'),
                ),
                Row(
                    Column('payment_method', css_class='form-group col-md-4 mb-0'),
                    Column('reference_number', css_class='form-group col-md-4 mb-0 ref-num-col'),
                    Column('payment_date', css_class='form-group col-md-4 mb-0'),
                ),
                HTML('<hr class="my-4">'),
            ),
            Div(
                HTML('<h6 class="mb-3 text-primary"><i class="bx bx-calendar me-1"></i>Period & Notes</h6>'),
                Row(
                    Column('period_start', css_class='form-group col-md-6 mb-0'),
                    Column('period_end', css_class='form-group col-md-6 mb-0'),
                ),
                'notes',
            ),
        )
