import django_filters
from django.forms import TextInput

from .models import User, GenderChoice


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'username'}), lookup_expr='icontains')
    first_name = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'first name'}), lookup_expr='icontains')
    last_name = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'last name'}), lookup_expr='icontains')
    email = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'email'}), lookup_expr='icontains')
    cnic = django_filters.CharFilter(widget=TextInput(attrs={'placeholder': 'CNIC (e.g. 12345-1234567-1)'}), lookup_expr='icontains', label='CNIC')
    gender = django_filters.ChoiceFilter(
        choices=[('', 'All Genders')] + list(GenderChoice.choices),
        empty_label=None,
        label='Gender',
    )

    class Meta:
        model = User
        fields = {}