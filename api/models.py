from django.db import models
from core.models import CustomUser, Profile

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.FieldFile(uploadto_to="course-file", blank=True, null=True, default="default.jpg")
    full_name = models.CharField(max_length=150)
    bio = models.CharField(max_length=150, null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=150, null=True, blank=True)
    
    def __str__(self):
        return self.full_name
    
    def students(self):
        return CartOrderItem.objects.filter(teacher=self)
    def courses(self):
        return Course.objects.filter(teacher=self)