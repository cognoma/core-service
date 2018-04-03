from rest_framework.test import APITestCase, APIClient

from api.models import Sample, Disease, Mutation, Gene

class SampleTests(APITestCase):
    sample_keys = ['sample_id',
                   'disease',
                   'mutations',
                   'gender',
                   'age_diagnosed']

    def setUp(self):
        self.gene1 = Gene.objects.create(entrez_gene_id=123456,
                                         symbol='GENE123',
                                         description='foo',
                                         chromosome='1',
                                         gene_type='bar',
                                         synonyms=['foo', 'bar'],
                                         aliases=['foo', 'bar'])
        self.gene2 = Gene.objects.create(entrez_gene_id=123457,
                                         symbol='GENE1234',
                                         description='fooo',
                                         chromosome='12',
                                         gene_type='barr',
                                         synonyms=['fooo', 'barr'],
                                         aliases=['fooo', 'barr'])
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
        self.sample3 = Sample.objects.create(sample_id='TCGA-2G-AALW-02',
                                             disease=self.disease1,
                                             gender='male',
                                             age_diagnosed=43)
        self.sample4 = Sample.objects.create(sample_id='TCGA-2G-AALW-03',
                                             disease=self.disease1,
                                             gender='male',
                                             age_diagnosed=42)
        self.mutation1 = Mutation.objects.create(gene=self.gene1,
                                                 sample=self.sample1)
        self.mutation2 = Mutation.objects.create(gene=self.gene1,
                                                 sample=self.sample2)
        self.mutation3 = Mutation.objects.create(gene=self.gene2,
                                                 sample=self.sample3)

    def test_list_samples(self):
        client = APIClient()

        list_response = client.get('/samples')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 4)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.sample_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.sample_keys)

    def test_get_sample(self):
        client = APIClient()

        get_response = client.get('/samples/' + str(self.sample1.sample_id))

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(list(get_response.data.keys()), self.sample_keys)

    def test_single_gene_query(self):
        client = APIClient()

        get_response = client.get('/samples', {
                                  'disease': self.disease1.acronym,
                                  'any_mutations': str(self.gene2.entrez_gene_id),
                                  })

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data['results']), 1)
        expected_samples = [self.sample3.sample_id,]
        returned_samples = [x['sample_id'] for x in get_response.data['results']]
        self.assertEqual(expected_samples, returned_samples)

    def test_multi_gene_query_order_invariant(self):
        client = APIClient()

        get_response1 = client.get('/samples', {
                                  'disease': self.disease1.acronym,
                                  'any_mutations':
                                      ','.join([str(self.gene1.entrez_gene_id), str(self.gene2.entrez_gene_id)]),
                                  })
        self.assertEqual(get_response1.status_code, 200)

        get_response2 = client.get('/samples', {
                                  'disease': self.disease1.acronym,
                                  'any_mutations':
                                      ','.join([str(self.gene2.entrez_gene_id), str(self.gene1.entrez_gene_id)]),
                                  })
        self.assertEqual(get_response2.status_code, 200)

        self.assertEqual(get_response1.data['results'], get_response2.data['results'])

    def test_multi_gene_query(self):
        client = APIClient()

        get_response = client.get('/samples', {
                                  'disease': self.disease1.acronym,
                                  'any_mutations':
                                      ','.join([str(self.gene2.entrez_gene_id), str(self.gene1.entrez_gene_id)]),
                                  })

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data['results']), 3)
        expected_samples = [self.sample1.sample_id, self.sample2.sample_id,
            self.sample3.sample_id,]
        returned_samples = [x['sample_id'] for x in get_response.data['results']]
        self.assertEqual(sorted(expected_samples), sorted(returned_samples))
