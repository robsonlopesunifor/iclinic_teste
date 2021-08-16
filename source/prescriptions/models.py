from uuid import uuid4
from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.



class Prescriptions(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    clinic = JSONField()
    physician = JSONField()
    patient = JSONField()
    text = models.CharField(max_length=80)

    def __str__(self):
        return f"prescriptions {self.id}"