from django.urls import path
from .views import MemberOnboardingWizard
from .forms import WizardMemberForm, WizardPaymentForm
from src.services.accounts.forms import UserCreateForm

app_name = 'onboarding'

urlpatterns = [
    path(
        '',
        MemberOnboardingWizard.as_view([UserCreateForm, WizardMemberForm, WizardPaymentForm]),
        name='start',
    ),
]
