import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    # Customizing the default Django user to be tenant-aware
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

