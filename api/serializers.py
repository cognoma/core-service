from datetime import datetime, timezone
import string
import random

from rest_framework import serializers
from api.models import User, Classifier, Disease, Sample, Mutation
from genes.models import Gene, Organism

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    email = serializers.CharField(required=False, allow_blank=False, max_length=255)
    last_login = serializers.DateTimeField(read_only=True, format='iso-8601')
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    def create(self, validated_data):
        ## 25 charcters to get 128bit unique random slug
        slug = "".join([random.SystemRandom().choice(string.ascii_lowercase + string.digits) for n in range(25)])

        validated_data['random_slugs'] = [slug]
        validated_data['last_login'] = datetime.now(timezone.utc)

        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

    def to_representation(self, obj):
        output = serializers.Serializer.to_representation(self, obj)

        ## Only return secure random slug on create
        if self.context['request'].method == 'POST':
            output['random_slugs'] = obj.random_slugs

        return output

class ClassifierSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    genes = serializers.PrimaryKeyRelatedField(required=True, many=True, queryset=Gene.objects.all())
    diseases = serializers.PrimaryKeyRelatedField(required=False, many=True, queryset=Disease.objects.all())
    user = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    task_id = serializers.IntegerField(read_only=True)
    results = serializers.JSONField(required=False)
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    def create(self, validated_data):
        return Classifier.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.genes = validated_data.get('genes', instance.genes)
        instance.diseases = validated_data.get('diseases', instance.diseases)
        instance.results = validated_data.get('results', instance.results)
        instance.save()
        return instance

class OrganismSerializer(serializers.Serializer):
    taxonomy_id = serializers.IntegerField()
    common_name = serializers.CharField()
    scientific_name = serializers.CharField()
    slug = serializers.CharField()

class GeneSerializer(serializers.Serializer):
    entrezid = serializers.IntegerField()
    systematic_name = serializers.CharField()
    standard_name = serializers.CharField()
    description = serializers.CharField()
    organism = OrganismSerializer()
    aliases = serializers.CharField()
    obsolete = serializers.BooleanField()

class DiseaseSerializer(serializers.Serializer):
    acronym = serializers.CharField()
    name = serializers.CharField()

class MutationSerializer(serializers.Serializer):
    gene_id = serializers.PrimaryKeyRelatedField(queryset=Gene.objects.all())
    sample_id = serializers.PrimaryKeyRelatedField(queryset=Sample.objects.all())
    status = serializers.BooleanField()

class SampleSerializer(serializers.Serializer):
    sample_id = serializers.CharField()
    disease = DiseaseSerializer(many=True)
    mutations = MutationSerializer(many=True)
    gender = serializers.CharField()
    age_diagnosed = serializers.IntegerField()

