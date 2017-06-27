import django_filters
from rest_framework import filters
from rest_framework import generics

from api.models import User, Classifier, Disease, Sample, Mutation, Gene
from api import serializers
from api.auth import UserUpdateSelfOnly, ClassifierPermission

# Classifier

class ClassifierFilter(filters.FilterSet):
    created_at__gte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='lte')

    updated_at__gte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='lte')

    class Meta:
        model = Classifier
        fields = ['user', 'created_at', 'updated_at']

class ClassifierListCreate(generics.ListCreateAPIView):
    permission_classes = (ClassifierPermission,)
    queryset = Classifier.objects.all()
    serializer_class = serializers.ClassifierSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ClassifierFilter
    ordering_fields = ('user', 'created_at', 'updated_at')
    ordering = ('created_at',)

class ClassifierRetrieveUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = (ClassifierPermission,)
    queryset = Classifier.objects.all()
    serializer_class = serializers.ClassifierSerializer
    lookup_field = 'id'

# User

class UserFilter(filters.FilterSet):
    created_at__gte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='lte')

    updated_at__gte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['email', 'created_at', 'updated_at']

class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = UserFilter
    ordering_fields = ('created_at', 'updated_at')
    ordering = ('created_at',)

class UserSlugListCreate(generics.ListCreateAPIView):
    def get_queryset(self):
        random_slug = self.kwargs['random_slug']
        return User.objects.filter(random_slugs__contains='{'+random_slug+'}')

    permission_classes = (UserUpdateSelfOnly,)
    serializer_class   = serializers.UserSerializer

class UserRetrieveUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = (UserUpdateSelfOnly,)
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'id'

# Genes

class GeneFilter(filters.FilterSet):
    class Meta:
        model = Gene
        fields = ['entrez_gene_id', 'symbol', 'chromosome', 'gene_type']

class GeneList(generics.ListAPIView):
    queryset = Gene.objects.all()
    serializer_class = serializers.GeneSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = GeneFilter
    ordering_fields = ('entrez_gene_id', 'symbol', 'chromosome')
    ordering = ('entrez_gene_id',)

class GeneRetrieve(generics.RetrieveAPIView):
    queryset = Gene.objects.all()
    serializer_class = serializers.GeneSerializer
    lookup_field = 'entrez_gene_id'

# Diseases

class DiseaseFilter(filters.FilterSet):
    class Meta:
        model = Disease
        fields = ['acronym', 'name']

class DiseaseList(generics.ListAPIView):
    queryset = Disease.objects.all()
    serializer_class = serializers.DiseaseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = DiseaseFilter
    ordering_fields = ('acronym', 'name',)
    ordering = ('acronym',)

class DiseaseRetrieve(generics.RetrieveAPIView):
    queryset = Disease.objects.all()
    serializer_class = serializers.DiseaseSerializer
    lookup_field = 'acronym'

# Mutations

class MutationFilter(filters.FilterSet):
    class Meta:
        model = Mutation
        fields = ['gene', 'sample']

class MutationList(generics.ListAPIView):
    queryset = Mutation.objects.all()
    serializer_class = serializers.MutationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MutationFilter
    ordering_fields = ('id',)
    ordering = ('id',)

class MutationRetrieve(generics.RetrieveAPIView):
    queryset = Mutation.objects.all()
    serializer_class = serializers.MutationSerializer
    lookup_field = 'id'

# Samples

class SampleFilter(filters.FilterSet):
    age_diagnosed__gte = django_filters.IsoDateTimeFilter(name='age_diagnosed', lookup_expr='gte')
    age_diagnosed__lte = django_filters.IsoDateTimeFilter(name='age_diagnosed', lookup_expr='lte')

    class Meta:
        model = Sample
        fields = ['sample_id', 'disease', 'gender', 'age_diagnosed', 'mutations__gene', 'mutations__gene__entrez_gene_id']

class SampleList(generics.ListAPIView):
    queryset = Sample.objects.all()
    serializer_class = serializers.SampleSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SampleFilter
    ordering_fields = ('sample_id', 'disease', 'age_diagnosed',)
    ordering = ('sample_id',)

class SampleRetrieve(generics.RetrieveAPIView):
    queryset = Sample.objects.all()
    serializer_class = serializers.SampleSerializer
    lookup_field = 'sample_id'
