from django.db import models
from django.urls import reverse
from django.utils import timezone


class Topic(models.Model):
    name = models.CharField(max_length=150, unique=True)
    order_no = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order_no"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("journal:view_story", kwargs={"topic_id": self.pk})


class Story(models.Model):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="stories",
    )
    heading = models.CharField(max_length=250)
    description = models.TextField(
        help_text="Write in Markdown. You may insert HTML img/video/source tags where needed."
    )
    desktop_background_url = models.URLField(
        blank=True,
        null=True,
        help_text="Desktop background image URL (16:9)"
    )

    mobile_background_url = models.URLField(
        blank=True,
        null=True,
        help_text="Mobile background image URL (9:16)"
    )
    story_datetime = models.DateTimeField(default=timezone.now, verbose_name="Date and time")
    order_no = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order_no"]

    def __str__(self):
        return self.heading

    def get_absolute_url(self):
        return reverse("journal:detail_story", kwargs={"story_id": self.pk})
