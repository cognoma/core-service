import datetime
from django.core.mail import send_mail
from django.conf import settings
import django_filters
from rest_framework import filters, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.pagination import LimitOffsetPagination

from api.auth import UserAccessSelfOnly, ClassifierCreatePermission, ClassifierRetrievePermission, MLWorkerOnlyPermission
from api.models import User, Classifier, Disease, Sample, Mutation, Gene
from api.serializers import ClassifierSerializer, UserSerializer, GeneSerializer, DiseaseSerializer, MutationSerializer, SampleSerializer
from api import queue

# Classifier

class ClassifierFilter(filters.FilterSet):
    created_at__gte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='lte')

    updated_at__gte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='lte')

    class Meta:
        model = Classifier
        fields = ['user', 'created_at', 'updated_at']

class ClassifierCreate(generics.CreateAPIView):
    permission_classes = (ClassifierCreatePermission,)
    serializer_class = ClassifierSerializer

class RetrieveClassifier(generics.RetrieveAPIView):
    permission_classes = (ClassifierRetrievePermission,)
    queryset = Classifier.objects.all()
    serializer_class = ClassifierSerializer
    lookup_field = 'id'

class UploadCompletedNotebookToClassifier(APIView):
    permission_classes = (MLWorkerOnlyPermission,)

    def post(self, request, id):
        try:
            classifier = Classifier.objects.get(id=id)
        except Classifier.DoesNotExist:
            raise NotFound('Classifier not found')

        serializer = ClassifierSerializer(classifier,
                                          data={
                                              'notebook_file': request.FILES['notebook_file'],
                                              'completed_at': datetime.datetime.utcnow()
                                          }, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        download_link = classifier.notebook_file.url
        nbviewer_link = 'https://nbviewer.jupyter.org/urls/' + download_link.replace('https://', '')
        email_message = 'Cognoma has completed processing your classifier.\n' + \
                        'Visit {notebook_link} to download your notebook.\n'.format(notebook_link=download_link) + \
                        'Visit {nbviewer_link} to view your notebook online.'.format(nbviewer_link=nbviewer_link)
        send_mail(subject='Cognoma Classifier {id} Processing Complete'.format(id=classifier.id),
                  message=email_message,
                  from_email=settings.FROM_EMAIL,
                  recipient_list=[classifier.user.email],
                  fail_silently=True)
        return Response(serializer.data, status=201)

class PullClassifierTaskQueue(APIView):
    permission_classes = (MLWorkerOnlyPermission,)

    def get(self, request, format=None):
        if 'title' in request.query_params:
            title = request.query_params.getlist('title')
        else:
            raise ParseError('`title` query parameter required')

        if 'worker_id' in request.query_params:
            try:
                worker_id = str(request.query_params['worker_id'])
            except ValueError:
                raise ParseError('`worker_id` query parameter must be a string')
        else:
            raise ParseError('`worker_id` query parameter required')

        if 'limit' in request.query_params:
            try:
                limit = int(request.query_params['limit'])
            except ValueError:
                raise ParseError('`limit` query parameter must be an integer')
        else:
            limit = 1

        if limit < 1 or limit > 10:
            raise ParseError('`limit` must be between 1 and 10')

        raw_classifiers = queue.get_classifiers(title,
                                                worker_id,
                                                limit)

        classifiers = []
        for classifier in raw_classifiers:
            serializer = ClassifierSerializer(classifier)
            classifiers.append(serializer.data)

        return Response(classifiers)

class ReleaseClassifierTask(APIView):
    permission_classes = (MLWorkerOnlyPermission,)

    def post(self, request, id):
        try:
            classifier = Classifier.objects.get(id=id)
        except Classifier.DoesNotExist:
            raise NotFound('Task not found')

        classifier.status = 'queued'
        classifier.locked_at = None
        classifier.worker_id = None
        classifier.save()

        return Response(data={'message': 'Classifier task released.'}, status=200)

class FailClassifierTask(APIView):
    permission_classes = (MLWorkerOnlyPermission,)

    def post(self, request, id):
        try:
            classifier = Classifier.objects.get(id=id)
        except Classifier.DoesNotExist:
            raise NotFound('Task not found')
        serializer = ClassifierSerializer(classifier, data={
            'failed_at': datetime.datetime.utcnow(),
            'fail_reason': request.data['fail_reason'],
            'fail_message': request.data['fail_message']
        }, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if classifier.attempts >= classifier.max_attempts:
            email_message = 'An error has occurred and your classifier could not be processed.\n' + \
                            'Error: ' + classifier.fail_message + '\n' + \
                            'Support is available at https://github.com/cognoma.'
            send_mail(subject='Cognoma Classifier {id} Processing Failure'.format(id=classifier.id),
                      message=email_message,
                      from_email=settings.FROM_EMAIL,
                      recipient_list=[classifier.user.email],
                      fail_silently=True)

        return Response(data=serializer.data, status=200)

# User

class UserFilter(filters.FilterSet):
    created_at__gte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.IsoDateTimeFilter(name='created_at', lookup_expr='lte')

    updated_at__gte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='gte')
    updated_at__lte = django_filters.IsoDateTimeFilter(name='updated_at', lookup_expr='lte')

    class Meta:
        model = User
        fields = ['email', 'created_at', 'updated_at']

class UserCreate(generics.CreateAPIView):
    permission_classes = []
    serializer_class = UserSerializer

class UserRetrieveUpdate(generics.RetrieveUpdateAPIView):
    permission_classes = (UserAccessSelfOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

class UserRetrieveFromSlug(generics.RetrieveAPIView):
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'random_slugs'

    def get_object(self):
        random_slug = self.kwargs['random_slug']
        return self.queryset.get(random_slugs__contains=[random_slug])

# Genes

class GeneFilter(filters.FilterSet):
    class Meta:
        model = Gene
        fields = ['entrez_gene_id', 'symbol', 'chromosome', 'gene_type']

class GenePagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10

class GeneList(generics.ListAPIView):
    queryset = Gene.objects.all()
    serializer_class = GeneSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = GeneFilter
    pagination_class = GenePagination
    ordering_fields = ('entrez_gene_id', 'symbol', 'chromosome')
    ordering = ('entrez_gene_id',)

class GeneRetrieve(generics.RetrieveAPIView):
    queryset = Gene.objects.all()
    serializer_class = GeneSerializer
    lookup_field = 'entrez_gene_id'

# Diseases

class DiseaseFilter(filters.FilterSet):
    class Meta:
        model = Disease
        fields = ['acronym', 'name']

class DiseaseList(generics.ListAPIView):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = DiseaseFilter
    ordering_fields = ('acronym', 'name',)
    ordering = ('acronym',)

class DiseaseRetrieve(generics.RetrieveAPIView):
    queryset = Disease.objects.all()
    serializer_class = DiseaseSerializer
    lookup_field = 'acronym'

# Mutations

class MutationFilter(filters.FilterSet):
    class Meta:
        model = Mutation
        fields = ['gene', 'sample']

class MutationList(generics.ListAPIView):
    queryset = Mutation.objects.all()
    serializer_class = MutationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MutationFilter
    ordering_fields = ('id',)
    ordering = ('id',)

class MutationRetrieve(generics.RetrieveAPIView):
    queryset = Mutation.objects.all()
    serializer_class = MutationSerializer
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
    serializer_class = SampleSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SampleFilter
    ordering_fields = ('sample_id', 'disease', 'age_diagnosed',)
    ordering = ('sample_id',)

class SampleRetrieve(generics.RetrieveAPIView):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    lookup_field = 'sample_id'
