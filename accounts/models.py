from django.db import models
from django.contrib.auth.models import AbstractUser
from organization.models import Organization
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'), 
        ('MEMBER', 'Member'),
        ('OWNER', 'Owner'),
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True,related_name="users")
    role    = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')   
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_users'
    )

    def __str__(self):
        return self.username
    
