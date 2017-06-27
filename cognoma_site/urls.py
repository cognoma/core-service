from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^classifiers/?$', views.ClassifierListCreate.as_view()),
    url(r'^classifiers/(?P<id>[0-9]+)$', views.ClassifierRetrieveUpdate.as_view()),

    url(r'^users/?$', views.UserListCreate.as_view()),
    url(r'^users/(?P<id>[0-9]+)$', views.UserRetrieveUpdate.as_view()),
    url(r'^users/(?P<random_slug>.+)$', views.UserSlugListCreate.as_view()),
    

    url(r'^genes/?$', views.GeneList.as_view()),
    url(r'^genes/(?P<entrez_gene_id>[0-9]+)$', views.GeneRetrieve.as_view()),

    url(r'^diseases/?$', views.DiseaseList.as_view()),
    url(r'^diseases/(?P<acronym>[a-zA-Z]+)$', views.DiseaseRetrieve.as_view()),

    url(r'^mutations/?$', views.MutationList.as_view()),
    url(r'^mutations/(?P<id>[0-9]+)$', views.MutationRetrieve.as_view()),

    url(r'^samples/?$', views.SampleList.as_view()),
    url(r'^samples/(?P<sample_id>[A-Z0-9\-]+)$', views.SampleRetrieve.as_view()),
]
