from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres import fields as postgresfields

from genes.models import Gene

GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female")
)

class User(models.Model):
    class Meta:
        db_table = "users"

    # id added by default
    random_slugs = postgresfields.ArrayField(models.CharField(max_length=25))
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

class Mutation(models.Model):
    class Meta:
        db_table = "mutations"

    # id added by default
    gene = models.ForeignKey(Gene, related_name='mutations')
    sample = models.ForeignKey(Sample, related_name='mutations')
    status = models.BooleanField()

class Classifier(models.Model):
    class Meta:
        db_table = "classifiers"

    # id added by default
    genes = models.ManyToManyField(Gene)
    diseases = models.ManyToManyField(Disease)
    user = models.ForeignKey(User)
    task_id = models.IntegerField(null=False, blank=False)
    results = postgresfields.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
