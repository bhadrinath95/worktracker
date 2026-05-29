from .models import Notification
from django.utils import timezone
from datetime import timedelta


def active_notifications(request):
    today = timezone.localdate()

    notifications = Notification.objects.filter(
        is_completed=False,
        date__gte=today,
        date__lte=today + timedelta(days=7)
    ).order_by('date')

    return {
        'active_notifications': notifications
    }