from django.db import models
from django.utils import timezone
from datetime import timedelta
import os
import re
from urllib.parse import quote_plus
from datetime import datetime

class TaskType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Task(models.Model):
    STATUS_CHOICES = [
        ('Opened', 'Opened'),
        ('InProgress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Hold', 'Hold'),
    ]
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Opened')
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    started_date = models.DateField(default=timezone.localtime(), null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    completed_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(default=timezone.localtime(), null=True, blank=True)
    is_bookmark = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    @property
    def days_till_upcoming(self):
        today = timezone.localdate()
        dates = []

        if self.started_date and self.started_date >= today:
            dates.append(self.started_date)

        if self.target_date and self.target_date >= today:
            dates.append(self.target_date)

        for upd in self.updates.all():
            if upd.status not in ['Completed', 'Cancelled'] and upd.date and upd.date >= today:
                dates.append(upd.date)

        if not dates:
            return None
        
        return (min(dates) - today).days

    def save(self, *args, **kwargs):
        if self.status in ['Completed', 'Cancelled'] and not self.completed_date:
            self.completed_date = timezone.localtime()
        elif self.status != 'Completed':
            self.completed_date = None
        super().save(*args, **kwargs)

class UpdateTemplate(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class Update(models.Model):
    STATUS_CHOICES = [
        ('Opened', 'Opened'),
        ('InProgress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]
    REMINDER_CHOICE = [
        ('Days', 'Days'),
        ('Workweek', 'Workweek'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
    ]
    name = models.CharField(max_length=200, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='updates')
    date = models.DateField(default=timezone.localtime(), null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    description = models.TextField()
    is_check_box = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Opened')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_CHOICE, null=True, blank=True)
    can_store_reminder = models.BooleanField(default=False)
    date_to_remind = models.IntegerField(null=True, blank=True)
    auto_reminder_handle = models.BooleanField(default=True)

    def __str__(self):
        return f"Update on {self.task.name}"
    
    def get_google_calendar_url(self):
        if not self.date:
            return ""

        start_dt = datetime.combine(
            self.date,
            self.start_time or datetime.min.time()
        )

        end_dt = datetime.combine(
            self.date,
            self.end_time or self.start_time or datetime.min.time()
        )

        start_str = timezone.make_aware(start_dt).strftime("%Y%m%dT%H%M%S")
        end_str = timezone.make_aware(end_dt).strftime("%Y%m%dT%H%M%S")

        # "https://calendar.google.com/calendar/u/0/r/eventedit"
        return (
            "https://calendar.google.com/calendar/render"
            f"?action=TEMPLATE"
            f"?text={quote_plus(self.name or self.task.name or '')}"
            f"&dates={start_str}/{end_str}"
            f"&details={quote_plus(self.description or '')}"
            f"&ctz=Asia/Kolkata"
            "#Intent;scheme=https;package=com.google.android.calendar;end"
        )
    
class LifePrincipleTopic(models.Model):
    topic = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.topic
    
class LifePrinciple(models.Model):
    
    topic = models.ForeignKey(
        LifePrincipleTopic,
        on_delete=models.CASCADE,
        related_name="principle_topic",
        null=True,
        blank=True
    )
    principle = models.TextField()
    meaning = models.TextField()

    def __str__(self):
        return self.principle

class FileType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    extensions = models.TextField(
        help_text="Comma-separated extensions like .pdf,.docx,.jpg"
    )

    preview_html = models.TextField(
        help_text="""
            Use {{ url }} for file URL
            Use {{ filename }} for file name
        """
    )

    icon_class = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bootstrap icon class. Leave empty to show thumbnail."
    )

    def get_extensions_list(self):
        return [ext.strip().lower() for ext in self.extensions.split(",")]

    def __str__(self):
        return self.name
    
class Document(models.Model):
    update = models.ForeignKey(Update, on_delete=models.CASCADE, related_name='documents')
    filename = models.CharField(max_length=255)
    fileurl = models.CharField(max_length=255)
    filetype = models.ForeignKey(
        FileType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    is_web_link = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.fileurl = re.sub(
            r'[\u200e\u200f\u202a-\u202e]',
            '',
            self.fileurl
        )
        ext = os.path.splitext(self.fileurl)[1].lower()
        self.filetype = self.detect_file_type(ext)
        super().save(*args, **kwargs)

    @staticmethod
    def detect_file_type(extension):
        for ft in FileType.objects.all():
            if extension in ft.get_extensions_list():
                return ft
        return FileType.objects.filter(name="other").first()

    def github_url(self):
        if self.filetype.name != "other" and not self.is_web_link:
            return f"https://raw.githubusercontent.com/tenctech10c/Document/main/{self.fileurl}"
        return self.fileurl

    def render_preview(self):
        if not self.filetype:
            return "<p>Preview not available.</p>"

        return (
            self.filetype.preview_html
            .replace("{{ github_url }}", self.github_url())
            .replace("{{ filename }}", self.filename)
        )
    
    def __str__(self):
        return self.filename
    
class Prayer(models.Model):
    god_id = models.IntegerField(null=True, blank=True)
    god_name = models.CharField(max_length=100)
    god_photo_url = models.URLField()
    god_audio_url = models.URLField()
    god_icon_url = models.URLField()
    prayer = models.TextField()

    def __str__(self):
        return self.god_name
    
class Todo(models.Model):

    date = models.DateField()
    description = models.TextField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.description
    
class Notification(models.Model):
    description = models.TextField()
    date = models.DateField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.description

    @property
    def should_display(self):
        today = timezone.localdate()
        start_date = self.date - timedelta(days=7)

        return (
            not self.is_completed and
            start_date <= today <= self.date
        )