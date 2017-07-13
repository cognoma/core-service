import string
import random

from rest_framework import serializers, exceptions
from expander import ExpanderSerializerMixin
from drf_dynamic_fields import DynamicFieldsMixin
from django.conf import settings

from api.models import User, Classifier, Disease, Sample, Mutation, Gene, PRIORITY_CHOICES, DEFAULT_CLASSIFIER_TITLE

class UniqueTaskConflict(exceptions.APIException):
    status_code = 409
    default_detail = 'Task `unique` field conflict'

class UserSerializer(DynamicFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    email = serializers.CharField(required=False, allow_blank=False, max_length=255)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    random_slugs = serializers.ListField(read_only=True, child=serializers.CharField(max_length=25))
    classifier_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        # 25 characters to get 128bit unique random slug
        slug = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for n in range(25))

        validated_data['random_slugs'] = [slug]

        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

    def to_representation(self, obj):
        output = serializers.Serializer.to_representation(self, obj)

        if self.context['request'].auth and self.context['request'].auth['type']:
            auth_type = self.context['request'].auth['type']
        else:
            auth_type = None

        if (self.context['request'].method != 'POST' and
            auth_type != 'JWT' and
            (not self.context['request'].user or
             (auth_type != 'Bearer' and
              self.context['request'].user.id != obj.id))):
           del output['email']

        # Only return secure random slug on create
        if self.context['request'].method == 'POST':
            output['random_slugs'] = obj.random_slugs

        return output

class MutationSerializer(DynamicFieldsMixin, ExpanderSerializerMixin, serializers.Serializer):
    id = serializers.IntegerField()
    gene = serializers.PrimaryKeyRelatedField(queryset=Gene.objects.all())
    sample = serializers.PrimaryKeyRelatedField(queryset=Sample.objects.all())

class GeneSerializer(DynamicFieldsMixin, ExpanderSerializerMixin, serializers.Serializer):
    class Meta:
        expandable_fields = {
            'mutations': (MutationSerializer, (), {'many': True})
        }

    entrez_gene_id = serializers.IntegerField()
    symbol = serializers.CharField()
    description = serializers.CharField()
    chromosome = serializers.CharField()
    gene_type = serializers.CharField()
    synonyms = serializers.ListField(child=serializers.CharField(allow_blank=True))
    aliases = serializers.ListField(child=serializers.CharField(allow_blank=True))
    mutations = serializers.PrimaryKeyRelatedField(many=True, queryset=Mutation.objects.all())

class MutationSerializerMeta:
    expandable_fields = {
        'gene': GeneSerializer,
    }

MutationSerializer.Meta = MutationSerializerMeta

class DiseaseSerializer(DynamicFieldsMixin, serializers.Serializer):
    acronym = serializers.CharField()
    name = serializers.CharField()

class ClassifierSerializer(DynamicFieldsMixin, ExpanderSerializerMixin, serializers.Serializer):
    class Meta:
        expandable_fields = {
            'genes': (GeneSerializer, (), {'many': True}),
            'diseases': (DiseaseSerializer, (), {'many': True}),
            'user': UserSerializer
        }

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=False, max_length=255)
    name = serializers.CharField(required=False, allow_null=False, allow_blank=False, max_length=255)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=False, max_length=2048)
    genes = serializers.PrimaryKeyRelatedField(required=True, many=True, queryset=Gene.objects.all())
    diseases = serializers.PrimaryKeyRelatedField(required=False, many=True, queryset=Disease.objects.all())
    user = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    notebook_file = serializers.FileField(required=False, allow_empty_file=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    status = serializers.CharField(read_only=True)
    worker_id = serializers.CharField(read_only=True)
    priority = serializers.ChoiceField(required=False, choices=PRIORITY_CHOICES, read_only=True)
    timeout = serializers.IntegerField(required=False, read_only=True)
    attempts = serializers.IntegerField(read_only=True)
    max_attempts = serializers.IntegerField(required=False, read_only=True)
    locked_at = serializers.DateTimeField(format='iso-8601', read_only=True)
    started_at = serializers.DateTimeField(required=False, allow_null=True, format='iso-8601', input_formats=['iso-8601'])
    completed_at = serializers.DateTimeField(required=False, allow_null=True, format='iso-8601', input_formats=['iso-8601'])
    failed_at = serializers.DateTimeField(required=False, allow_null=True, format='iso-8601', input_formats=['iso-8601'])

    def create(self, validated_data):
        if self.context['request'].auth['type'] == 'JWT':
            if 'user' not in validated_data:
                raise exceptions.ValidationError({'user': 'Required when using an internal service token'})

            user = validated_data['user']
        else:
            user = self.context['request'].user

        classifier = Classifier()

        classifier.user = user
        classifier.title = validated_data.get('title', DEFAULT_CLASSIFIER_TITLE)
        classifier.name = validated_data.get('name')
        classifier.description = validated_data.get('description')
        classifier.save()

        if 'genes' in validated_data:
            for gene in validated_data['genes']:
                classifier.genes.add(gene)
        else:
            raise exceptions.ValidationError({'diseases': 'At least 1 gene is required.'})

        if 'diseases' in validated_data:
            for disease in validated_data['diseases']:
                classifier.diseases.add(disease)
        else:
            raise exceptions.ValidationError({'diseases': 'At least 1 disease is required.'})

        classifier.save()
        return classifier

    def update(self, instance, validated_data):
        failed_at = validated_data.get('failed_at', None)
        completed_at = validated_data.get('completed_at', None)

        if failed_at is None and completed_at is not None:
            instance.status = 'complete'
        elif failed_at is not None and completed_at is None:
            if instance.attempts >= instance.max_attempts:
                instance.status = 'failed'
            else:
                instance.status = 'failed_retrying'
        elif failed_at is not None and completed_at is not None:
            raise exceptions.ValidationError('`failed_at` and `completed_at` cannot be both non-null at the same time.')

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.completed_at = completed_at
        instance.failed_at = failed_at
        instance.notebook_file = validated_data.get('notebook_file', instance.notebook_file)

        instance.save()
        return instance

class SampleSerializer(DynamicFieldsMixin, ExpanderSerializerMixin, serializers.Serializer):
    class Meta:
        expandable_fields = {
            'disease': DiseaseSerializer,
            'mutations': (MutationSerializer, (), {'many': True})
        }

    sample_id = serializers.CharField()
    disease = serializers.PrimaryKeyRelatedField(queryset=Disease.objects.all())
    mutations = serializers.PrimaryKeyRelatedField(many=True, queryset=Mutation.objects.all())
    gender = serializers.CharField()
    age_diagnosed = serializers.IntegerField()

