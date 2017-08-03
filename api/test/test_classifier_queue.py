import os
from datetime import datetime, timedelta
from unittest.mock import patch

from django.conf import settings
from rest_framework.test import APITestCase, APIClient

from api.test.test_classifiers import classifier_keys
from api.models import Classifier, Gene, Disease, DEFAULT_CLASSIFIER_TITLE

number_of_classifiers_created_initially = 1
error_reason = 'default_error'
error_message = 'Classifier processing failed.'

class ClassifierQueueTests(APITestCase):

    @patch('django.utils.timezone.now')
    def setUp(self, mocked_now):
        # now needs to be padded to account for API and db clocks not in perfect sync
        test_datetime = (datetime.utcnow() - timedelta(0, 3)).isoformat() + 'Z'

        mocked_now.return_value = test_datetime

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

        self.classifier_title = 'classifier-search'

        self.classifier_create_client = APIClient()
        self.classifier_create_client.credentials(HTTP_AUTHORIZATION=self.token)

        self.schedule_classifier()

    def schedule_classifier(self, priority=None, max_attempts=1):
        classifier_post_data = {
            'genes': [self.gene1.entrez_gene_id, self.gene2.entrez_gene_id],
            'diseases': [self.disease1.acronym, self.disease2.acronym]
        }

        response = self.classifier_create_client.post('/classifiers', classifier_post_data, format='json')
        self.assertEqual(response.status_code, 201)

        classifier = Classifier.objects.get(id=response.data['id'])
        classifier.max_attempts = max_attempts
        if priority is not None:
            classifier.priority = priority
        classifier.save()

        return response.data

    def test_pull_from_queue(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(list(response.data[0].keys()), classifier_keys)

        self.assertEqual(response.data[0]['status'], 'in_progress')
        self.assertEqual(response.data[0]['worker_id'], 'foo')

    def test_pull_from_queue_auth(self):
        client = APIClient()

        response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

        client.credentials(HTTP_AUTHORIZATION=self.token)
        response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')
        self.assertEqual(response.status_code, 403)

    def test_pull_from_queue_with_limit(self):
        client = APIClient()
        
        limit = 10
        
        for x in range(0, limit - number_of_classifiers_created_initially + 1):
            self.schedule_classifier()
        
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo&limit='
                              + str(limit))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), limit)

        for classifier in response.data:
            self.assertEqual(list(classifier.keys()), classifier_keys)

    @patch('django.utils.timezone.now')
    def test_pull_from_queue_order(self, mocked_now):
        # now needs to be padded to account for API and db clocks not in perfect sync
        test_datetime = (datetime.utcnow() - timedelta(0, 3)).isoformat() + 'Z'

        mocked_now.return_value = test_datetime

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        minus_10_min = (datetime.utcnow() - timedelta(0, 600)).isoformat() + 'Z'

        # purposely not ordered by the actual expected by pull
        classifier4 = self.schedule_classifier(priority=4)
        classifier1 = self.schedule_classifier(priority=1)
        classifier2 = self.schedule_classifier(priority=2)

        response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')
        self.assertEqual(classifier1['id'], response.data[0]['id'])

        response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')
        self.assertEqual(classifier2['id'], response.data[0]['id'])

        # All the 'normal' priority tasks from setUp() should be here
        response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), number_of_classifiers_created_initially)

        response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')
        self.assertEqual(classifier4['id'], response.data[0]['id'])

    def test_release_classifier(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        classifier_queue_response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')
        self.assertEqual(classifier_queue_response.status_code, 200)
        self.assertEqual(len(classifier_queue_response.data), 1)

        classifier = classifier_queue_response.data[0]

        self.assertEqual(classifier['status'], 'in_progress')

        release_response = client.post('/classifiers/' + str(classifier['id']) + '/release')
        self.assertEqual(release_response.status_code, 200)

        classifier_response = client.get('/classifiers/' + str(classifier['id']))
        self.assertEqual(classifier_response.status_code, 200)

        self.assertEqual(classifier_response.data['status'], 'queued')

    def pull_and_update(self, client, is_fail):
        classifier_queue_response = client.get('/classifiers/queue?title=' + DEFAULT_CLASSIFIER_TITLE + '&worker_id=foo')
        self.assertEqual(classifier_queue_response.status_code, 200)
        self.assertEqual(len(classifier_queue_response.data), 1)

        classifier = classifier_queue_response.data[0]

        if is_fail:
            update_response = client.post('/classifiers/{id}/fail/'.format(id=classifier['id']), data={
                'fail_reason': error_reason,
                'fail_message': error_message
            }, format='json')
            self.assertEqual(update_response.status_code, 200)
        else:
            with open(os.path.join(settings.BASE_DIR, 'api/test/fixtures/test_notebook.ipynb'), mode='rb') as notebook_file:
                path = '/classifiers/{id}/upload/'.format(id=classifier['id'])
                update_response = client.post(path,
                                              data={'notebook_file': notebook_file},
                                              format='multipart')
                self.assertEqual(update_response.status_code, 201)

        return update_response

    def test_pull_and_complete(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        update_response = self.pull_and_update(client, False)

        self.assertEqual(update_response.data['status'], 'complete')

    def test_pull_and_fail(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        update_response = self.pull_and_update(client, True)

        self.assertEqual(update_response.data['status'], 'failed')
        self.assertEqual(update_response.data['fail_reason'], error_reason)
        self.assertEqual(update_response.data['fail_message'], error_message)

    def test_pull_retry_fail(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        self.schedule_classifier(1, max_attempts=3)

        # fail #1
        response = self.pull_and_update(client, True)
        self.assertEqual(response.data['status'], 'failed_retrying')
        self.assertEqual(response.data['attempts'], 1)

        # fail #2
        response = self.pull_and_update(client, True)
        self.assertEqual(response.data['status'], 'failed_retrying')
        self.assertEqual(response.data['attempts'], 2)

        # fail #3
        response = self.pull_and_update(client, True)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['attempts'], 3)

    def test_pull_retry_complete(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.service_token)

        self.schedule_classifier(1, max_attempts=3)

        # fail #1
        response = self.pull_and_update(client, True)
        self.assertEqual(response.data['status'], 'failed_retrying')
        self.assertEqual(response.data['attempts'], 1)

        # fail #2
        response = self.pull_and_update(client, True)
        self.assertEqual(response.data['status'], 'failed_retrying')
        self.assertEqual(response.data['attempts'], 2)

        # complete
        response = self.pull_and_update(client, False)
        self.assertEqual(response.data['status'], 'complete')
        self.assertEqual(response.data['attempts'], 3)

    def test_upload_notebook_from_user(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        with open(os.path.join(settings.BASE_DIR, 'api/test/fixtures/test_notebook.ipynb'), mode='rb') as notebook_file:
            path = '/classifiers/{id}/upload/'.format(id=1)
            upload_response = client.post(path,
                                          data={'notebook_file': notebook_file},
                                          format='multipart')
        self.assertEqual(upload_response.status_code, 403)

    def test_upload_notebook_from_internal_service(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token)

        classifier_create_response = client.post('/classifiers', self.classifier_post_data, format='json')
        self.assertEqual(classifier_create_response.status_code, 201)
        classifier_id = classifier_create_response.data['id']

        client.credentials(HTTP_AUTHORIZATION=self.service_token)
        with open(os.path.join(settings.BASE_DIR, 'api/test/fixtures/test_notebook.ipynb'), mode='rb') as notebook_file:
            path = '/classifiers/{id}/upload/'.format(id=classifier_id)
            upload_response = client.post(path,
                                          data={'notebook_file': notebook_file},
                                          format='multipart')
        self.assertEqual(upload_response.status_code, 201)
        classifier = Classifier.objects.get(id=classifier_id)
        self.assertIsNotNone(classifier.notebook_file.name)
        self.assertEqual(upload_response.data['status'], 'complete')

