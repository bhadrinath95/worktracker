from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    special_privilege_password = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.user)