# Generated by Django 5.0 on 2024-01-08 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Annotations',
            fields=[
                ('annot_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('annot_type', models.CharField(max_length=256)),
                ('created_by', models.CharField(max_length=256, null=True)),
                ('creation_date', models.DateField()),
                ('data', models.JSONField()),
                ('instance_id', models.CharField(max_length=512)),
                ('modality', models.CharField(max_length=256)),
                ('series_id', models.CharField(max_length=512)),
                ('slice', models.IntegerField()),
                ('study_id', models.CharField(max_length=512)),
                ('title', models.CharField(max_length=512)),
                ('parameters', models.JSONField()),
                ('slices_number', models.IntegerField()),
                ('version', models.IntegerField()),
            ],
            options={
                'db_table': 'annotation',
                'indexes': [models.Index(fields=['study_id'], name='idx_annotation_study_id'), models.Index(fields=['version'], name='idx_annotation_version')],
            },
        ),
        migrations.CreateModel(
            name='Annotationsversion',
            fields=[
                ('annot_version_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('study_id', models.CharField(max_length=512)),
                ('version', models.IntegerField()),
                ('created_by', models.CharField(max_length=256)),
                ('creation_date', models.DateField()),
            ],
            options={
                'db_table': 'annotation_version',
                'indexes': [models.Index(fields=['study_id'], name='idx_annot_v_study_id'), models.Index(fields=['version'], name='idx_annot_v_version')],
            },
        ),
    ]