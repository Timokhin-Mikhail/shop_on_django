from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, blank=False, default='bronze')
    balance = models.PositiveIntegerField(default=0, null=False)
    purchase_amount = models.PositiveBigIntegerField(default=0, null=False)



