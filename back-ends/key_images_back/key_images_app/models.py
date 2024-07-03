from django.db import models


class Keyimages(models.Model):
    keyimageuid = models.CharField(primary_key=True, max_length=512)
    patientid = models.CharField(max_length=512, blank=True, null=True)
    studyuid = models.CharField(max_length=512, blank=True, null=True)
    seriename = models.CharField(max_length=512, blank=True, null=True)
    seriesuid = models.CharField(max_length=512, blank=True, null=True)
    ismultiframe = models.BooleanField(blank=True, null=True)
    instanceuid = models.CharField(max_length=512, blank=True, null=True)
    slice = models.IntegerField(blank=True, null=True)
    wadouri = models.CharField(max_length=512)
    timestamp = models.DateTimeField(blank=True, null=True)
    isfusion = models.BooleanField(blank=True, null=True)
    backlayer = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'keyimages'
        indexes = [
            models.Index(fields=['studyuid'], name='idx_study'),
            models.Index(fields=['patientid'], name='idx_patient_id'),
        ] 

