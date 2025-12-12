from django.db import models
from tracker.models import LifePrinciple, LifePrincipleTopic


# ---------------- Main Statement ----------------

class Statement(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("inprogress", "In-Progress"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=255)
    statement_text = models.TextField()

    conclusion = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ---------------- Options for Each Statement ----------------

class StatementOption(models.Model):
    AGREE_CHOICES = [
        ("agree", "Agree"),
        ("disagree", "Disagree"),
    ]

    statement = models.ForeignKey(
        Statement,
        on_delete=models.CASCADE,
        related_name="options"
    )

    option_description = models.TextField()

    # agree/disagree
    decision = models.CharField(
        max_length=20,
        choices=AGREE_CHOICES, 
        null=True, blank=True
    )

    # multiple principles that justify the option
    cancelled_principles = models.ManyToManyField(
        LifePrinciple,
        blank=True
    )

    # If the option is influenced by someone
    advice_from = models.CharField(max_length=255, null=True, blank=True)
    advice_reason = models.TextField(null=True, blank=True)
    advice_is_link = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.statement.title} - {self.decision}"
