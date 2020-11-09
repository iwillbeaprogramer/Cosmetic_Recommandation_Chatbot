import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mychatsite.settings")

from django.conf import settings
from django.db import models

# Create your models here.
class Info(models.Model):
    user_id = models.CharField(max_length=10, null=False, primary_key=True)
    step = models.IntegerField(null=False)
    tag = models.CharField(max_length=10, null=True)
    category = models.CharField(max_length=20, null=True)
    result = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.user_id+"/"+str(self.step)+"/"+self.tag+"/"+self.result)

