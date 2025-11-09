from django.db import models
from django.utils import timezone
from datetime import timedelta

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
    ]
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Opened')
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    started_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    completed_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.status == 'Completed' and not self.completed_date:
            self.completed_date = timezone.now()
        elif self.status != 'Completed':
            self.completed_date = None
        super().save(*args, **kwargs)


class Update(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='updates')
    date = models.DateField(default=timezone.now)
    description = models.TextField()

    def __str__(self):
        return f"Update on {self.task.name} - {self.date.strftime('%Y-%m-%d')}"
    
class LifePrinciple(models.Model):
    principle = models.TextField()
    meaning = models.TextField()

    def __str__(self):
        return self.principle
