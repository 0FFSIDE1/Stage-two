from django.db import models
import uuid
from django.contrib.auth.hashers import make_password
# from django.contrib.auth import get_user_model
# Create your models here.


class User(models.Model):
    user_Id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstName = models.CharField(max_length=15, null=False, default=None)
    lastName = models.CharField(max_length=15, null=False, default=None)
    email = models.EmailField(max_length=30,unique=True, null=False, default=None)
    password = models.CharField(max_length=200, default=None, null=False)
    phone = models.CharField(max_length=15, default=None)

    def __str__(self) -> str:
        return f"user_id: {self.user_Id}"

    
class Organisation(models.Model):
    orgId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, default=None, null=False, blank=True)
    description = models.CharField(max_length=100, default=None, blank=True, null=True)
    user = models.ManyToManyField(User, related_name='user_organisation')
    def __str__(self) -> str:
        return f"{self.name}"