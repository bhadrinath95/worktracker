from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from copy import copy

from tracker.models import Update

class Command(BaseCommand):
    help = "Process daily reminders"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        updates = Update.objects.filter(
            date=today,
            status="Opened",
            reminder_type__in=["Days", "Workweek"],
            date_to_remind=1
        )

        for update in updates:

            if update.can_store_reminder:
                update_copy = copy(update)
                update_copy.pk = None
                update_copy.date = today
                update_copy.is_check_box = False
                update_copy.status = "Cancelled"
                update_copy.save()

            # Move original date forward
            update.date = update.date + timedelta(days=update.date_to_remind)
            update.save()
            self.stdout.write(self.style.SUCCESS(f"'{update.description}' is updated successfully"))

        self.stdout.write(self.style.SUCCESS("Reminders processed successfully"))