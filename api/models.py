from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.core.validators import RegexValidator
from django.utils import timezone

DEFAULT_CLASSIFIER_TITLE = 'classifier-search'

GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female")
)

STATUS_CHOICES = (
    ("queued", "Queued"),
    ("in_progress", "In Progress"),
    ("failed_retrying", "Failed - Retrying"),
    ("dequeued", "Dequeued"),
    ("failed", "Failed"),
    ("completed", "Completed")
)

PRIORITY_CHOICES = (
    (1, "Critical"),
    (2, "High"),
    (3, "Normal"),
    (4, "Low")
)

class User(models.Model):
    class Meta:
        db_table = "users"

    # id added by default
    random_slugs = postgres_fields.ArrayField(models.CharField(max_length=25))
    name = models.CharField(null=True, max_length=255, blank=True)
    email = models.CharField(null=True, max_length=2048, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Disease(models.Model):
    class Meta:
        db_table = "diseases"

    acronym = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255, null=False, blank=False)

class Sample(models.Model):
    class Meta:
        db_table = "samples"

    sample_id = models.CharField(primary_key=True, max_length=255) # ID assigned by TCGA
    disease = models.ForeignKey(Disease)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, null=True)
    age_diagnosed = models.IntegerField(null=True, blank=False)

class Gene(models.Model):
    class Meta:
        db_table = "cognoma_genes"

    entrez_gene_id = models.IntegerField(primary_key=True)
    symbol = models.TextField()
    description = models.TextField()
    chromosome = models.TextField(null=True)
    gene_type = models.TextField()
    synonyms = postgres_fields.ArrayField(models.TextField(), null=True)
    aliases = postgres_fields.ArrayField(models.TextField(), null=True)

class Mutation(models.Model):
    class Meta:
        db_table = "mutations"

    # id added by default
    gene = models.ForeignKey(Gene, related_name='mutations')
    sample = models.ForeignKey(Sample, related_name='mutations')

class Classifier(models.Model):
    class Meta:
        db_table = "classifiers"

    def classifier_notebook_file_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/notebooks/classifier_<id>.ipynb
        return 'notebooks/classifier_{0}.ipynb'.format(instance.id)

    # id added by default
    title = models.CharField( # ex "classifier-search"
        max_length=255,
        validators=[
            RegexValidator(
                regex='^[a-z0-9\-_]+$',
                message='Classifier type can only contain lowercase alphanumeric characters, dashes, and underscores.',
            )
        ],
        default=DEFAULT_CLASSIFIER_TITLE
    )
    name = models.CharField('optional name', null=True, max_length=255, blank=False)
    description = models.CharField('optional description', null=True, max_length=2048, blank=False)
    genes = models.ManyToManyField(Gene)
    diseases = models.ManyToManyField(Disease)
    user = models.ForeignKey(User)
    notebook_file = models.FileField(null=True, upload_to=classifier_notebook_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(choices=STATUS_CHOICES, max_length=17, default='queued')
    worker_id = models.CharField(null=True, max_length=255)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=3)
    timeout = models.IntegerField('timeout in seconds', default=600)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField('max number of times this job can attempt to run', default=1)
    fail_reason = models.CharField(null=True, max_length=255)
    fail_message = models.CharField(null=True, max_length=1000)
    locked_at = models.DateTimeField(null=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    failed_at = models.DateTimeField(null=True)
