from src.services.accounts.models import User, Instructor
from src.services.finance.models import Member, Payment, Expense, SubscriptionPlan, GymShift
from src.apps.whisper.models import EmailNotification

MODEL_CLASS_LOOKUP = {
    'accounts': {
        'user': User,
        'instructor': Instructor,
    },
    'finance': {
        'member': Member,
        'payment': Payment,
        'expense': Expense,
        'subscriptionplan': SubscriptionPlan,
        'gymshift': GymShift,
    },
    'whisper': {
        'emailnotification': EmailNotification,
    },
}
