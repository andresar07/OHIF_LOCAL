from django.db import models

# Create your models here.

class Annotations(models.Model):
    annot_id = models.BigAutoField(primary_key=True)
    annot_type = models.CharField(max_length=256, null=False)
    created_by = models.CharField(max_length=256, null=True)
    creation_date = models.DateField(auto_now_add=False)
    data = models.JSONField()
    instance_id = models.CharField(max_length=512)
    modality = models.CharField(max_length=256)
    series_id = models.CharField(max_length=512)
    slice = models.IntegerField()
    study_id = models.CharField(max_length=512)
    title = models.CharField(max_length=512)
    parameters = models.JSONField()
    slices_number = models.IntegerField()
    version = models.IntegerField()

    class Meta:
        db_table = 'annotation'
        indexes = [
            models.Index(fields=['study_id'], name='idx_annotation_study_id'),
            models.Index(fields=['version'], name='idx_annotation_version'),
        ]

class Annotationsversion(models.Model):
    annot_version_id = models.BigAutoField(primary_key=True)
    study_id = models.CharField(max_length=512, null=False)
    version = models.IntegerField(null=False)
    created_by = models.CharField(max_length=256)
    creation_date = models.DateField(auto_now_add=False)

    class Meta:
        db_table = 'annotation_version'
        indexes = [
            models.Index(fields=['study_id'], name='idx_annot_v_study_id'),
            models.Index(fields=['version'], name='idx_annot_v_version'),
        ]



