import django_filters
from rest_framework import filters
from rest_framework import generics

from api.models import User, Classifier
from genes.models import Gene, Organism
from api.serializers import UserSerializer, ClassifierSerializer, OrganismSerializer, GeneSerializer

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
    queryset = Classifier.objects.all()
    serializer_class = ClassifierSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ClassifierFilter
    ordering_fields = ('user', 'created_at', 'updated_at')
    ordering = ('created_at',)

class ClassifierRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = Classifier.objects.all()
    serializer_class = ClassifierSerializer
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
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = UserFilter
    ordering_fields = ('created_at', 'updated_at')
    ordering = ('created_at',)

class UserRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

# Genes

class GeneFilter(filters.FilterSet):
    class Meta:
        model = Gene
        fields = ['entrezid', 'systematic_name', 'standard_name', 'aliases', 'obsolete']

class GeneList(generics.ListAPIView):
    queryset = Gene.objects.all()
    serializer_class = GeneSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = GeneFilter
    ordering_fields = ('entrezid', 'systematic_name', 'standard_name')
    ordering = ('entrezid',)

class GeneRetrieve(generics.RetrieveAPIView):
    queryset = Gene.objects.all()
    serializer_class = GeneSerializer
    lookup_field = 'entrezid'

# Organisms

class OrganismFilter(filters.FilterSet):
    class Meta:
        model = Organism
        fields = ['taxonomy_id', 'common_name', 'scientific_name', 'slug']

class OrganismList(generics.ListAPIView):
    queryset = Organism.objects.all()
    serializer_class = OrganismSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = OrganismFilter
    ordering_fields = ('taxonomy_id', 'common_name', 'scientific_name')
    ordering = ('taxonomy_id',)

class OrganismRetrieve(generics.RetrieveAPIView):
    queryset = Organism.objects.all()
    serializer_class = OrganismSerializer
    lookup_field = 'taxonomy_id'
