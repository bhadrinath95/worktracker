from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from copy import copy
from datetime import date, timedelta
from calendar import monthrange

from tracker.models import Update, Todo

class Command(BaseCommand):
    help = "Process daily reminders"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        updates = Update.objects.filter(
            date=today,
            status="Opened"
        ).exclude(
            reminder_type__isnull=True
        ).exclude(
            reminder_type=""
        ).exclude(
            auto_reminder_handle=False
        )

        for update in updates:

            if update.can_store_reminder:
                update_copy = copy(update)
                update_copy.pk = None
                update_copy.date = today
                update_copy.is_check_box = False
                update_copy.status = "Cancelled"
                update_copy.save()

            if update.reminder_type == 'Monthly':
                year = update.date.year
                month = update.date.month + 1
                if month == 13:
                    month = 1
                    year += 1
                day = update.date_to_remind
                try:
                    update.date = date(year, month, day)
                except ValueError:
                    update.date = date(year, month, monthrange(year, month)[1])

            elif update.reminder_type == 'Yearly':
                year = update.date.year + 1
                month = update.date.month
                day = update.date_to_remind or update.date.day
                update.date_to_remind = day
                try:
                    update.date = date(year, month, day)
                except ValueError:
                    update.date = date(year, month, monthrange(year, month)[1])

            elif update.reminder_type == 'Weekly':
                current_weekday = (update.date.weekday() + 1) % 7
                target_weekday = update.date_to_remind
                days_ahead = target_weekday - current_weekday
                if days_ahead <= 0:
                    days_ahead += 7
                update.date += timedelta(days=days_ahead)

            elif update.reminder_type == 'Workweek':
                next_date = update.date + timedelta(days=1)
                if next_date.weekday() == 5:   
                    next_date += timedelta(days=2)
                elif next_date.weekday() == 6:
                    next_date += timedelta(days=1)
                update.date = next_date
                
            elif update.reminder_type == 'Days':
                update.date += timedelta(days=update.date_to_remind)

            else:
                update.date = today
                update.status = "Cancelled"
            update.save()
            self.stdout.write(self.style.SUCCESS(f"'{update.description}' is updated successfully"))

        self.stdout.write(self.style.SUCCESS("Reminders processed successfully"))

        cutoff_date = today - timedelta(days=3)

        deleted_count, _ = Todo.objects.filter(
            is_completed=True,
            date__lt=cutoff_date
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(f"{deleted_count} completed todos older than 3 days deleted")
        )

        self.stdout.write(self.style.SUCCESS("Reminders processed successfully"))