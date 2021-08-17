from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.


class Prescriptions(models.Model):
    clinic = JSONField()
    physician = JSONField()
    patient = JSONField()
    text = models.CharField(max_length=80)

    def __str__(self):
        return f"prescriptions {self.id}"
