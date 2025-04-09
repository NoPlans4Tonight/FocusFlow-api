from django.db import models
from django.contrib.auth.models import User
import secrets
from django.utils.timezone import now

class Workspace(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_workspaces")
    members = models.ManyToManyField(User, related_name="workspaces")

    def __str__(self):
        return self.name

class APIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="api_key", null=True)
    key = models.CharField(max_length=64, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(48)  # Generate a secure 64-char API key
        super().save(*args, **kwargs)

    def __str__(self):
        return f"APIKey for {self.user.username}"

class ContextEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="context_entries", null=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="context_entries", null=True)
    activity = models.CharField(max_length=255)
    note = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.activity} ({self.start_time})"

class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    api_token = models.CharField(max_length=255, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.api_token:
            self.api_token = secrets.token_urlsafe(48)  # Generate a secure API token
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
