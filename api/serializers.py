import string
import random

from rest_framework import serializers, exceptions
from expander import ExpanderSerializerMixin
from drf_dynamic_fields import DynamicFieldsMixin
from django.contrib.postgres import fields as postgresfields
from api.models import User, Classifier, Disease, Sample, Mutation, Gene


class UserSerializer(DynamicFieldsMixin, serializers.Serializer):
    id           = serializers.IntegerField(read_only=True)
    name         = serializers.CharField(required=False, allow_blank=True, max_length=255)
    email        = serializers.CharField(required=False, allow_blank=False, max_length=255)
    created_at   = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at   = serializers.DateTimeField(read_only=True, format='iso-8601')
    random_slugs = postgresfields.ArrayField(serializers.CharField(max_length=25))

    def create(self, validated_data):
        ## 25 charcters to get 128bit unique random slug
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

        ## Only return secure random slug on authenticated GET requests
        if (auth_type == 'Bearer' and self.context['request'].method == 'GET' ):
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
    genes = serializers.PrimaryKeyRelatedField(required=True, many=True, queryset=Gene.objects.all())
    diseases = serializers.PrimaryKeyRelatedField(required=False, many=True, queryset=Disease.objects.all())
    user = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    task_id = serializers.IntegerField(read_only=True)
    results = serializers.JSONField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    def create(self, validated_data):
        if self.context['request'].auth['type'] == 'JWT':
            if 'user' not in validated_data:
                raise exceptions.ValidationError({'user': 'Required when using an internal service token'})

            user = validated_data['user']
        else:
            user = self.context['request'].user

        classifier_input = {
            'user': user, # force loggedin user id
            'task_id': 234 # TODO: create task
        }

        if 'results' in validated_data:
            classifier_input['results'] = validated_data['results']

        classifier =  Classifier.objects.create(**classifier_input)

        if 'genes' in validated_data:
            for gene in validated_data['genes']:
                classifier.genes.add(gene)

        if 'diseases' in validated_data:
            for disease in validated_data['diseases']:
                classifier.diseases.add(disease)

        return classifier

    def update(self, instance, validated_data):
        instance.genes = validated_data.get('genes', instance.genes)
        instance.diseases = validated_data.get('diseases', instance.diseases)
        instance.results = validated_data.get('results', instance.results)
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
