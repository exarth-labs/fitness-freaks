from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from datetime import timedelta

from .filters import SubscriptionPlanFilter, MemberFilter, PaymentFilter, ExpenseFilter
from .forms import SubscriptionPlanForm, GymShiftForm, MemberForm, PaymentForm, ExpenseForm, RenewSubscriptionForm
from .mixins import FinanceListViewMixin, FinanceDetailViewMixin, FinanceDeleteViewMixin, FinanceCreateViewMixin, FinanceUpdateViewMixin
from .models import SubscriptionPlan, GymShift, Member, Payment, Expense, SubscriptionStatus, PaymentStatus


""" GYM SHIFT VIEWS """


class GymShiftListView(FinanceListViewMixin):
    model = GymShift
    filter_class = None


class GymShiftCreateView(FinanceCreateViewMixin, CreateView):
    model = GymShift
    form_class = GymShiftForm
    template_name = 'finance/gymshift_form.html'

    def get_success_url(self):
        messages.success(self.request, "Gym shift created successfully.")
        return reverse_lazy('finance:gymshift_list')


class GymShiftUpdateView(FinanceUpdateViewMixin, UpdateView):
    model = GymShift
    form_class = GymShiftForm
    template_name = 'finance/gymshift_form.html'

    def get_success_url(self):
        messages.success(self.request, "Gym shift updated successfully.")
        return reverse_lazy('finance:gymshift_list')


class GymShiftDeleteView(FinanceDeleteViewMixin, DeleteView):
    model = GymShift
    template_name = 'finance/gymshift_confirm_delete.html'
    success_url = reverse_lazy('finance:gymshift_list')


""" SUBSCRIPTION PLAN VIEWS """


class SubscriptionPlanListView(FinanceListViewMixin):
    model = SubscriptionPlan
    filter_class = SubscriptionPlanFilter


class SubscriptionPlanCreateView(FinanceCreateViewMixin, CreateView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanForm
    template_name = 'finance/subscriptionplan_form.html'

    def get_success_url(self):
        messages.success(self.request, "Subscription plan created successfully.")
        return reverse_lazy('finance:subscriptionplan_list')


class SubscriptionPlanUpdateView(FinanceUpdateViewMixin, UpdateView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanForm
    template_name = 'finance/subscriptionplan_form.html'

    def get_success_url(self):
        messages.success(self.request, "Subscription plan updated successfully.")
        return reverse_lazy('finance:subscriptionplan_list')


class SubscriptionPlanDeleteView(FinanceDeleteViewMixin, DeleteView):
    model = SubscriptionPlan
    template_name = 'finance/subscriptionplan_confirm_delete.html'
    success_url = reverse_lazy('finance:subscriptionplan_list')


""" MEMBER VIEWS """


class MemberListView(FinanceListViewMixin):
    model = Member
    filter_class = MemberFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        # Update expired statuses
        today = timezone.now().date()
        queryset.filter(
            subscription_end__lt=today,
            status=SubscriptionStatus.ACTIVE
        ).update(status=SubscriptionStatus.EXPIRED)
        return queryset


class MemberDetailView(FinanceDetailViewMixin, DetailView):
    model = Member
    template_name = 'finance/member_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()[:10]
        context['renew_form'] = RenewSubscriptionForm(
            initial={'subscription_plan': self.object.subscription_plan}
        )
        return context


class MemberCreateView(FinanceCreateViewMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = 'finance/member_form.html'

    def get_success_url(self):
        messages.success(self.request, "Member created successfully.")
        return reverse_lazy('finance:member_detail', kwargs={'pk': self.object.pk})


class MemberUpdateView(FinanceUpdateViewMixin, UpdateView):
    model = Member
    form_class = MemberForm
    template_name = 'finance/member_form.html'

    def get_success_url(self):
        messages.success(self.request, "Member updated successfully.")
        return reverse_lazy('finance:member_detail', kwargs={'pk': self.object.pk})


class MemberDeleteView(FinanceDeleteViewMixin, DeleteView):
    model = Member
    template_name = 'finance/member_confirm_delete.html'
    success_url = reverse_lazy('finance:member_list')


""" PAYMENT VIEWS """


class PaymentListView(FinanceListViewMixin):
    model = Payment
    filter_class = PaymentFilter


class PaymentDetailView(FinanceDetailViewMixin, DetailView):
    model = Payment
    template_name = 'finance/payment_detail.html'


class PaymentCreateView(FinanceCreateViewMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'finance/payment_form.html'

    def form_valid(self, form):
        form.instance.received_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Payment recorded successfully.")
        return reverse_lazy('finance:payment_detail', kwargs={'pk': self.object.pk})


class PaymentUpdateView(FinanceUpdateViewMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'finance/payment_form.html'

    def get_success_url(self):
        messages.success(self.request, "Payment updated successfully.")
        return reverse_lazy('finance:payment_list')


class PaymentDeleteView(FinanceDeleteViewMixin, DeleteView):
    model = Payment
    template_name = 'finance/payment_confirm_delete.html'
    success_url = reverse_lazy('finance:payment_list')


""" EXPENSE VIEWS """


class ExpenseListView(FinanceListViewMixin):
    model = Expense
    filter_class = ExpenseFilter


class ExpenseCreateView(FinanceCreateViewMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance/expense_form.html'

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Expense recorded successfully.")
        return reverse_lazy('finance:expense_list')


class ExpenseUpdateView(FinanceUpdateViewMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance/expense_form.html'

    def get_success_url(self):
        messages.success(self.request, "Expense updated successfully.")
        return reverse_lazy('finance:expense_list')


class ExpenseDeleteView(FinanceDeleteViewMixin, DeleteView):
    model = Expense
    template_name = 'finance/expense_confirm_delete.html'
    success_url = reverse_lazy('finance:expense_list')


""" QUICK ACTIONS """


class RenewMemberSubscriptionView(FinanceCreateViewMixin, CreateView):
    """Renew a member's subscription - separate page view"""
    model = Payment
    form_class = RenewSubscriptionForm
    template_name = 'finance/member_renew.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member'] = get_object_or_404(Member, pk=self.kwargs.get('pk'))
        return context

    def form_valid(self, form):
        member = get_object_or_404(Member, pk=self.kwargs.get('pk'))
        plan = form.cleaned_data['subscription_plan']

        # Calculate new subscription period
        today = timezone.now().date()
        if member.subscription_end and member.subscription_end > today:
            period_start = member.subscription_end
        else:
            period_start = today
        period_end = period_start + timedelta(days=plan.duration_days)

        # Create payment
        payment = Payment.objects.create(
            member=member,
            subscription_plan=plan,
            amount=form.cleaned_data['amount'],
            discount=form.cleaned_data.get('discount') or 0,
            payment_method=form.cleaned_data['payment_method'],
            reference_number=form.cleaned_data.get('reference_number'),
            notes=form.cleaned_data.get('notes'),
            period_start=period_start,
            period_end=period_end,
            status=PaymentStatus.PAID,
            received_by=self.request.user
        )

        messages.success(self.request, f'Subscription renewed successfully until {period_end}')
        self.object = payment
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('finance:member_detail', kwargs={'pk': self.kwargs.get('pk')})

