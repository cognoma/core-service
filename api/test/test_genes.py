from rest_framework.test import APITestCase, APIClient

from api.models import Gene

class GeneTests(APITestCase):
    gene_keys = ['entrez_gene_id',
                 'symbol',
                 'description',
                 'chromosome',
                 'gene_type',
                 'synonyms',
                 'aliases',
                 'mutations']

    def setUp(self):
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

        get_response = client.get('/genes/' + str(self.gene1.entrez_gene_id))

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(list(get_response.data.keys()), self.gene_keys)

    def test_entrezid_filter(self):
        client = APIClient()

        list_response = client.get('/genes?entrez_gene_id=123456')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 1)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.gene_keys)
        self.assertEqual(list_response.data['results'][0]['entrez_gene_id'], 123456)
