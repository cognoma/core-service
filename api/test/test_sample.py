from rest_framework.test import APITestCase, APIClient

from api.models import Sample, Disease, Mutation
from genes.models import Gene, Organism

class SampleTests(APITestCase):
    sample_keys = ['sample_id',
                   'disease',
                   'mutations',
                   'gender',
                   'age_diagnosed']

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
                                                 sample=self.sample1,
                                                 status=True)
        self.mutation2 = Mutation.objects.create(gene=self.gene1,
                                                 sample=self.sample2,
                                                 status=True)

    def test_list_samples(self):
        client = APIClient()

        list_response = client.get('/samples')

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list(list_response.data.keys()), ['count',
                                                           'next',
                                                           'previous',
                                                           'results'])
        self.assertEqual(len(list_response.data['results']), 2)
        self.assertEqual(list(list_response.data['results'][0].keys()), self.sample_keys)
        self.assertEqual(list(list_response.data['results'][1].keys()), self.sample_keys)

    def test_get_sample(self):
        client = APIClient()

        get_response = client.get('/samples/' + str(self.sample1.sample_id))

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(list(get_response.data.keys()), self.sample_keys)

