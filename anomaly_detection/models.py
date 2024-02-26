from django.db import models
from django.contrib.postgres.fields import ArrayField

class Predictions(models.Model):

    timestamp_from = models.DateTimeField(blank=True, null=True)
    timestamp_to = models.DateTimeField(blank=True, null=True)
    ip = ArrayField(models.CharField(max_length=250, blank=True, null=True))
    ip_status = ArrayField(models.FloatField(blank=True, null=True))