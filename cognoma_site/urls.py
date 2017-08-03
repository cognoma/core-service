from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_swagger.views import get_swagger_view
from api import views

schema_view = get_swagger_view(title='Cognoma API')

urlpatterns = [
    url(r'^$', schema_view),

    url(r'^classifiers/?$', views.ClassifierCreate.as_view()),
    url(r'^classifiers/queue/?$', views.PullClassifierTaskQueue.as_view()),
    url(r'^classifiers/(?P<id>[0-9]+)$', views.RetrieveClassifier.as_view()),
    url(r'^classifiers/(?P<id>[0-9]+)/upload/?$', views.UploadCompletedNotebookToClassifier.as_view()),
    url(r'^classifiers/(?P<id>[0-9]+)/release/?$', views.ReleaseClassifierTask.as_view()),
    url(r'^classifiers/(?P<id>[0-9]+)/fail/?$', views.FailClassifierTask.as_view()),

    url(r'^users/?$', views.UserCreate.as_view()),
    url(r'^users/(?P<id>[0-9]+)$', views.UserRetrieveUpdate.as_view()),
    url(r'^users/(?P<random_slug>.+)$', views.UserRetrieveFromSlug.as_view()),

    # url(r'^genes/?$', views.GeneList.as_view()),
    # url(r'^genes/(?P<entrez_gene_id>[0-9]+)$', views.GeneRetrieve.as_view()),

    url(r'^diseases/?$', views.DiseaseList.as_view()),
    url(r'^diseases/(?P<acronym>[a-zA-Z]+)$', views.DiseaseRetrieve.as_view()),

    # url(r'^mutations/?$', views.MutationList.as_view()),
    # url(r'^mutations/(?P<id>[0-9]+)$', views.MutationRetrieve.as_view()),

    url(r'^samples/?$', views.SampleList.as_view()),
    url(r'^samples/(?P<sample_id>[A-Z0-9\-]+)$', views.SampleRetrieve.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
