from rest_framework.test import APITestCase, APIClient

from genes.models import Gene, Organism

class GeneTests(APITestCase):
    gene_keys = ['id',
                 'entrezid',
                 'systematic_name',
                 'standard_name',
                 'description',
                 'organism',
                 'aliases',
                 'obsolete',
                 'mutations']

    def setUp(self):
        self.human = Organism.objects.create(taxonomy_id=123,
                                             common_name='human',
                                             scientific_name='homo sapien',
                                             slug='homo-sapien')
        self.gene1 = Gene.objects.create(entrezid=123456,
                                         systematic_name='foo',
                                         description='bar',
                                         aliases='foo, bar',
                                         obsolete=False,
                                         weight=1.0,
                                         organism_id=self.human.id)
        self.gene2 = Gene.objects.create(entrezid=234567,
                                         systematic_name='foo',
                                         description='bar',
                                         aliases='foo, bar',
                                         obsolete=False,
                                         weight=1.0,
                                         organism_id=self.human.id)

    def test_list_genes(self):
        client = APIClient()

        list_response = client.get('/genes')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.gene_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.gene_keys)

    def test_get_gene(self):
        client = APIClient()

        get_response = client.get('/genes/' + str(self.gene1.id))

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(list(get_response.data.keys()), self.gene_keys)

    def test_entrezid_filter(self):
        client = APIClient()

        list_response = client.get('/genes?entrezid=123456')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 1)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.gene_keys)
        self.assertEqual(list_response.data['results'][0]['entrezid'], 123456)

