from rest_framework.test import APITestCase, APIClient

from genes.models import Gene, Organism

class OrganismTests(APITestCase):
    organism_keys = ['id',
                     'taxonomy_id',
                     'common_name',
                     'scientific_name',
                     'slug']

    def setUp(self):
        self.human = Organism.objects.create(taxonomy_id=123,
                                             common_name='human',
                                             scientific_name='homo sapien',
                                             slug='homo-sapien')
        self.awm33 = Organism.objects.create(taxonomy_id=234,
                                             common_name='awm33',
                                             scientific_name='homo githubien',
                                             slug='homo-githubien')

    def test_list_organisms(self):
        client = APIClient()

        list_response = client.get('/organisms')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.organism_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.organism_keys)

    def test_get_organism(self):
        client = APIClient()

        get_response = client.get('/organisms/' + str(self.human.id))

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(list(get_response.data.keys()), self.organism_keys)

    def test_taxonomy_id_filter(self):
        client = APIClient()

        list_response = client.get('/organisms?taxonomy_id=234')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 1)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.organism_keys)
        self.assertEqual(list_response.data['results'][0]['taxonomy_id'], 234)

