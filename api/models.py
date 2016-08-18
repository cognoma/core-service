from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres import fields as postgresfields

from genes.models import Gene

class User(models.Model):
    class Meta:
        db_table = "users"

    # id added by default
    random_slugs = postgresfields.ArrayField(models.CharField(max_length=16))
    name = models.CharField(null=True, max_length=255, blank=True)
    email = models.CharField(null=True, max_length=2048, blank=False)
    last_login = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Algorithm(models.Model):
    class Meta:
        db_table = "algorithms"

    name = models.CharField(primary_key=True, max_length=255)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.CharField(max_length=2048, null=False, blank=False)

class Classifier(models.Model):
    class Meta:
        db_table = "classifiers"

    # id added by default
    algorithm = models.ForeignKey(Algorithm, db_column="algorithm", null=False, blank=False)
    expression_genes = models.ForeignKey(Gene)
    # tissues = models.ForeignKey(Tissue)
    user = models.ForeignKey(User)
    task_id = models.IntegerField(null=False, blank=False)
    results = postgresfields.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
