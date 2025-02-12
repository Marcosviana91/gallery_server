from django.db import models
from django.contrib.auth.models import User

from uuid import uuid4

# Create your models here.

class Device(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    unique_key = models.UUIDField(null=False, blank=True)
    description = models.TextField(null=False, blank=False)
    shortname = models.CharField(max_length=25, blank=False, null=False)
    
    def save(self, *args, **kwargs):
        if not self.unique_key:
            self.unique_key = f'{self.user.id}-{uuid4()}'
        super().save(*args, **kwargs)