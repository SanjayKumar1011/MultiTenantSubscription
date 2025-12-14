from django.db import models
from django.contrib.auth.models import AbstractUser
from organization.models import Organization

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'), 
        ('MEMBER', 'Member'),
        ('OWNER', 'Owner'),
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True,related_name="users")
    role    = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')   


    def __str__(self):
        return self.username
    
