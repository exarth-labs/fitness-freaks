from decimal import Decimal

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from src.services.accounts.forms import UserCreateForm
from src.services.accounts.mixins import StaffMixin
from src.services.finance.models import Member, Payment
from .forms import WizardMemberForm, WizardPaymentForm

STEP_TITLES = [
    "Create User Account",
    "Add Member Profile",
    "Record First Payment",
]


class MemberOnboardingWizard(StaffMixin, SessionWizardView):
    form_list = [UserCreateForm, WizardMemberForm, WizardPaymentForm]
    template_name = 'onboarding/wizard.html'

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)

        if step == '2':
            step1_data = self.get_cleaned_data_for_step('1') or {}
            plan = step1_data.get('subscription_plan')
            if plan:
                initial['subscription_plan'] = plan
                initial['amount'] = plan.price
            from src.core.models import Application
            app = Application.objects.first()
            if app and app.registration_fee:
                initial['registration_fee'] = app.registration_fee

        return initial

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        step = int(self.steps.current)
        context['step_title'] = STEP_TITLES[step]
        context['onboarding_step'] = step + 1

        if step >= 1:
            context['wizard_user_data'] = self.get_cleaned_data_for_step('0') or {}

        from src.core.models import Application
        app = Application.objects.first()
        context['registration_fee_help'] = str(app.registration_fee) if app else '0.00'

        return context

    def done(self, form_list, **kwargs):
        forms = list(form_list)

        # Step 1 — create User
        user = forms[0].save()

        # Step 2 — create Member linked to user
        member = forms[1].save(commit=False)
        member.user = user
        member.save()

        # Step 3 — create Payment linked to member
        payment = forms[2].save(commit=False)
        payment.member = member
        payment.received_by = self.request.user
        payment.save()

        messages.success(self.request, f"Member '{user.get_full_name() or user.email}' onboarded successfully!")
        return redirect(reverse_lazy('finance:member_detail', kwargs={'pk': member.pk}))
