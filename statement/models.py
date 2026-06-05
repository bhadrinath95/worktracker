from django.db import models


class DecisionTree(models.Model):
    name = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    
class Statement(models.Model):

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CURRENT = "CURRENT", "Current"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    tree = models.ForeignKey(
        DecisionTree,
        on_delete=models.CASCADE,
        related_name="nodes"
    )
    
    title = models.CharField(max_length=255)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"
    )

    description = models.TextField(
        blank=True,
        null=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title