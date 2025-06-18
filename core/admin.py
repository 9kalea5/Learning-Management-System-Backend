from django.contrib import admin
from .models import CustomUser, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name']
    ordering = ['full_name']
    
admin.site.register(CustomUser)
admin.site.register(Profile, ProfileAdmin)