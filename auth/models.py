from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    otp = models.CharField(unique=True, max_length=150)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS  = ['username']
    
    def __str__(self):
        return self.email