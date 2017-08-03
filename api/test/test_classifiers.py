import os
from unittest.mock import patch

from rest_framework.test import APITestCase, APIClient

from django.conf import settings

from api.models import Disease, Gene, Classifier

classifier_keys = ['id',
                   'title',
                   'name',
                   'description',
                   'genes',
                   'diseases',
                   'user',
                   'notebook_file',
                   'created_at',
                   'updated_at',
                   'status',
                   'worker_id',
                   'priority',
                   'timeout',
                   'attempts',
                   'max_attempts',
                   'fail_reason',
                   'fail_message',
                   'locked_at',
                   'started_at',
                   'completed_at',
                   'failed_at']

class ClassifierTests(APITestCase):

    def setUp(self):
        client = APIClient()

        user_response = client.post('/users', {}, format='json')
        self.assertEqual(user_response.status_code, 201)
        self.user = user_response.data

        self.token = 'Bearer ' + self.user['random_slugs'][0]

        self.gene1 = Gene.objects.create(entrez_gene_id=123456,
                                         symbol='GENE123',
                                         description='foo',
                                         chromosome='1',
                                         gene_type='bar',
                                         synonyms=['foo', 'bar'],
                                         aliases=['foo', 'bar'])
        self.gene2 = Gene.objects.create(entrez_gene_id=234567,
                                         symbol='GENE234',
                                         description='foo',
                                         chromosome='X',
                                         gene_type='bar',
                                         synonyms=['foo', 'bar'],
                                         aliases=['foo', 'bar'])
        self.disease1 = Disease.objects.create(acronym='BLCA',
                                               name='bladder urothelial carcinoma')
        self.disease2 = Disease.objects.create(acronym='GBM',
                                               name='glioblastoma multiforme')
        self.classifier_post_data = {
            'genes': [self.gene1.entrez_gene_id, self.gene2.entrez_gene_id],
            'diseases': [self.disease1.acronym, self.disease2.acronym]
        }

        self.service_token = 'JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXJ2aWNlIjoiY29yZSJ9.HHlbWMjo-Y__DGV0DAiCY7u85FuNtY8wpovcZ9ga-oCsLdM2H5iVSz1vKiWK8zxl7dSYltbnyTNMxXO2cDS81hr4ohycr7YYg5CaE5sA5id73ab5T145XEdF5X_HXoeczctGq7X3x9QYSn7O1fWJbPWcIrOCs6T2DrySsYgjgdAAnWnKedy_dYWJ0YtHY1bXH3Y7T126QqVlQ9ylHk6hmFMCtxMPbuAX4YBJsxwjWpMDpe13xbaU0Uqo5N47a2_vi0XzQ_tzH5esLeFDl236VqhHRTIRTKhPTtRbQmXXy1k-70AU1FJewVrQddxbzMXJLFclStIdG_vW1dWdqhh-hQ'

    def test_create_classifier(self):
        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION=self.token)

        response = client.post('/classifiers', self.classifier_post_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), classifier_keys)

    def test_create_from_internal_service(self):
        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        classifier_post_data = self.classifier_post_data.copy()
        classifier_post_data['user'] = self.user['id']

        response = client.post('/classifiers', classifier_post_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(list(response.data.keys()), classifier_keys)

    def test_update_classifier(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        create_response = client.post('/classifiers', self.classifier_post_data, format='json')

        self.assertEqual(create_response.status_code, 201)

        classifier = create_response.data

        results = {'test': {'data': 'testing...'}, 'foo': 'bar'}

        classifier['results'] = results

        update_response = client.put('/classifiers/' + str(classifier['id']), classifier, format='json')

        self.assertEqual(update_response.status_code, 405)
        # self.assertEqual(list(update_response.data.keys()), classifier_keys)
        # self.assertEqual(update_response.data['results'], results)

    def test_must_be_logged_in(self):
        client = APIClient()
        create1_response = client.post('/classifiers', self.classifier_post_data, format='json')

        self.assertEqual(create1_response.status_code, 401)

        client.credentials(HTTP_AUTHORIZATION=self.token)

        create2_response = client.post('/classifiers', self.classifier_post_data, format='json')

        self.assertEqual(create2_response.status_code, 201)

        classifier = create2_response.data

        update_response = client.put('/classifiers/' + str(classifier['id']), {}, format='json')

        self.assertEqual(update_response.status_code, 405)

    def test_no_classifier_update_allowed(self):
        client = APIClient()

        update_response = client.put('/classifiers/1', {}, format='json')

        self.assertEqual(update_response.status_code, 405)

    def test_cannot_update_other_user_classifier(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        create_response = client.post('/classifiers', self.classifier_post_data, format='json')

        self.assertEqual(create_response.status_code, 201)

        user2 = client.post('/users', {}, format='json').data
        token2 = 'Bearer ' + user2['random_slugs'][0]

        client.credentials(HTTP_AUTHORIZATION=token2)

        classifier = create_response.data

        update_response = client.put('/classifiers/' + str(classifier['id']), classifier, format='json')

        self.assertEqual(update_response.status_code, 405)

    def test_update_from_internal_service(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        create_response = client.post('/classifiers', self.classifier_post_data, format='json')

        self.assertEqual(create_response.status_code, 201)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        classifier = create_response.data

        results = {'test': {'data': 'testing...'}, 'foo': 'bar'}

        classifier['results'] = results

        update_response = client.put('/classifiers/' + str(classifier['id']), classifier, format='json')

        self.assertEqual(update_response.status_code, 405)
        # self.assertEqual(list(update_response.data.keys()), classifier_keys)
        # self.assertEqual(update_response.data['results'], results)

    def test_list_classifiers(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        classifier1_response = client.post('/classifiers', self.classifier_post_data, format='json')
        classifier2_response = client.post('/classifiers', self.classifier_post_data, format='json')

        self.assertEqual(classifier1_response.status_code, 201)
        self.assertEqual(classifier2_response.status_code, 201)

        client = APIClient() # clear token

        list_response = client.get('/classifiers')

        self.assertEqual(list_response.status_code, 401)

    def test_get_classifier(self):
        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION=self.token)
        create_classifier_response = client.post('/classifiers', self.classifier_post_data, format='json')
        self.assertEqual(create_classifier_response.status_code, 201)

        get_classifier_authenticated_response = client.get('/classifiers/' + str(create_classifier_response.data['id']))
        self.assertEqual(get_classifier_authenticated_response.status_code, 200)
        self.assertEqual(list(get_classifier_authenticated_response.data.keys()), classifier_keys)

        client.credentials(HTTP_AUTHORIZATION=self.service_token)
        get_classifier_jwt_auth_response = client.get('/classifiers/' + str(create_classifier_response.data['id']))
        self.assertEqual(get_classifier_jwt_auth_response.status_code, 200)
        self.assertEqual(list(get_classifier_jwt_auth_response.data.keys()), classifier_keys)

        # clear token
        client = APIClient()
        get_classifier_unauthenticated_response = client.get('/classifiers/' + str(create_classifier_response.data['id']))
        # a user's classifiers are private to them
        self.assertEqual(get_classifier_unauthenticated_response.status_code, 401)

    def test_expansion(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        classifier1_response = client.post('/classifiers', self.classifier_post_data, format='json')
        classifier2_response = client.post('/classifiers', self.classifier_post_data, format='json')

        self.assertEqual(classifier1_response.status_code, 201)
        self.assertEqual(classifier2_response.status_code, 201)

        get_1_response = client.get('/classifiers/{id}?expand=user,genes,diseases'.format(id=classifier1_response.data['id']))
        get_2_response = client.get('/classifiers/{id}?expand=user,genes,diseases'.format(id=classifier2_response.data['id']))

        self.assertEqual(get_1_response.status_code, 200)
        self.assertEqual(get_1_response.status_code, 200)

        self.assertEqual(list(get_1_response.data.keys()), classifier_keys)
        self.assertEqual(list(get_2_response.data.keys()), classifier_keys)

        self.assertTrue(isinstance(get_1_response.data['user'], dict))
        self.assertTrue(isinstance(get_2_response.data['user'], dict))

        self.assertTrue(isinstance(get_1_response.data['genes'][0], dict))
        self.assertTrue(isinstance(get_1_response.data['genes'][1], dict))
        self.assertTrue(isinstance(get_1_response.data['diseases'][0], dict))
        self.assertTrue(isinstance(get_1_response.data['diseases'][1], dict))

        self.assertTrue(isinstance(get_2_response.data['genes'][0], dict))
        self.assertTrue(isinstance(get_2_response.data['genes'][1], dict))
        self.assertTrue(isinstance(get_2_response.data['diseases'][0], dict))
        self.assertTrue(isinstance(get_2_response.data['diseases'][1], dict))
