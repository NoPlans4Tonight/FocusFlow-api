from django.db import models

class ContextEntry(models.Model):
    user_id = models.IntegerField()
    activity = models.CharField(max_length=255)
    note = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)