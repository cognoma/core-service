from rest_framework.test import APITestCase, APIClient

from api.models import Sample, Disease, Mutation, Gene

class MutationTests(APITestCase):
    mutation_keys = ['id',
                     'gene',
                     'sample']

    def setUp(self):
        self.gene1 = Gene.objects.create(entrez_gene_id=123456,
                                         symbol='GENE123',
                                         description='foo',
                                         chromosome='1',
                                         gene_type='bar',
                                         synonyms=['foo', 'bar'],
                                         aliases=['foo', 'bar'])
        self.disease1 = Disease.objects.create(acronym='BLCA',
                                               name='bladder urothelial carcinoma')
        self.sample1 = Sample.objects.create(sample_id='TCGA-22-4593-01',
                                             disease=self.disease1,
                                             gender='female',
                                             age_diagnosed=37)
        self.sample2 = Sample.objects.create(sample_id='TCGA-2G-AALW-01',
                                             disease=self.disease1,
                                             gender='male',
                                             age_diagnosed=43)

        self.mutation1 = Mutation.objects.create(gene=self.gene1,
                                                 sample=self.sample1)
        self.mutation2 = Mutation.objects.create(gene=self.gene1,
                                                 sample=self.sample2)

    def test_list_mutations(self):
        client = APIClient()

        list_response = client.get('/mutations')

        self.assertEqual(list_response.status_code, 404)
        # self.assertEqual(list(list_response.data.keys()), ['count',
        #                                                    'next',
        #                                                    'previous',
        #                                                    'results'])
        # self.assertEqual(len(list_response.data['results']), 2)
        # self.assertEqual(list(list_response.data['results'][0].keys()), self.mutation_keys)
        # self.assertEqual(list(list_response.data['results'][1].keys()), self.mutation_keys)

    def test_get_mutations(self):
        client = APIClient()

        get_response = client.get('/mutations/' + str(self.mutation1.id))

        self.assertEqual(get_response.status_code, 404)
        # self.assertEqual(list(get_response.data.keys()), self.mutation_keys)
