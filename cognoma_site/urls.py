from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^classifiers/?$', views.ClassifierListCreate.as_view()),
    url(r'^classifiers/(?P<id>[0-9]+)$', views.ClassifierRetrieveUpdate.as_view()),
    url(r'^users/?$', views.UserListCreate.as_view()),
    url(r'^users/(?P<id>[0-9]+)$', views.UserRetrieveUpdate.as_view()),
    url(r'^genes/?$', views.GeneList.as_view()),
    url(r'^genes/(?P<entrezid>[0-9]+)$', views.GeneRetrieve.as_view()),
    url(r'^organisms/?$', views.OrganismList.as_view()),
    url(r'^organisms/(?P<taxonomy_id>[0-9]+)$', views.OrganismRetrieve.as_view()),
]
