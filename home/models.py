from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class WarnerResponse(models.Model):
    ip = models.GenericIPAddressField()
    port = models.CharField(max_length=5)
    datetime = models.DateTimeField(auto_now_add=True)
    status_code_200 = models.IntegerField(default=0)
    external_status_code_200 =models.IntegerField(default=0)
    user =models.ForeignKey(User, on_delete=models.CASCADE)


class Input(models.Model):
    input_text=models.CharField(max_length=200)
    user = models.CharField(max_length=200)
    datetime = models.DateTimeField( default=datetime.datetime.now)
    send = models.BooleanField(default=False)