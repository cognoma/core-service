from rest_framework.test import APITestCase, APIClient

from api.models import Disease

class DiseaseTests(APITestCase):
    disease_keys = ['acronym',
                    'name']

    def setUp(self):
        self.disease1 = Disease.objects.create(acronym='BLCA',
                                               name='bladder urothelial carcinoma')
        self.disease2 = Disease.objects.create(acronym='GBM',
                                               name='glioblastoma multiforme')

    def test_list_diseases(self):
        client = APIClient()

        list_response = client.get('/diseases')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.disease_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.disease_keys)

    def test_get_disease(self):
        client = APIClient()

        get_response = client.get('/diseases/' + str(self.disease1.acronym))

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(list(get_response.data.keys()), self.disease_keys)
