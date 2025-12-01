from django.contrib import admin
from .models import UserProfile
from .forms import UserProfileAdminForm

class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm

admin.site.register(UserProfile, UserProfileAdmin)