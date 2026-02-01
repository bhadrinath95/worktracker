from django.db import models
from django.utils import timezone
from datetime import timedelta
import os

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
    started_date = models.DateField(default=timezone.now, null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    completed_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(default=timezone.now, null=True, blank=True)
    is_bookmark = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    @property
    def days_till_upcoming(self):
        today = timezone.now().date()
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
            self.completed_date = timezone.now()
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
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='updates')
    date = models.DateField(default=timezone.now, null=True, blank=True)
    description = models.TextField()
    is_check_box = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Opened')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_CHOICE, null=True, blank=True)
    can_store_reminder = models.BooleanField(default=False)
    date_to_remind = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Update on {self.task.name}"
    
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

class Document(models.Model):
    update = models.ForeignKey(Update, on_delete=models.CASCADE, related_name='documents')
    filename = models.CharField(max_length=255)
    fileurl = models.CharField(max_length=255)
    filetype = models.CharField(max_length=50, editable=False)

    def save(self, *args, **kwargs):
        ext = os.path.splitext(self.fileurl)[1].lower()
        if ext in ['.pdf', '.doc', '.docx']:
            self.filetype = 'pdf'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            self.filetype = 'image'
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            self.filetype = 'video'
        elif ext in ['.mp3', '.m4a']:
            self.filetype = 'audio'
        else:
            self.filetype = 'other'
        super().save(*args, **kwargs)

    def github_url(self):
        if self.filetype != "other":
            return f"https://raw.githubusercontent.com/tenctech10c/Document/main/{self.fileurl}"
        return self.fileurl

    def __str__(self):
        return self.filename