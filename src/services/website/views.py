from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta

from src.services.accounts.models import User


class HomeView(TemplateView):
    """Gym portfolio single-page website"""
    template_name = 'website/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get last logged in users (staff only, for display)
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        context['recently_active_staff'] = User.objects.filter(
            is_staff=True,
            last_login__gte=week_ago
        ).order_by('-last_login')[:5]
        
        return context
