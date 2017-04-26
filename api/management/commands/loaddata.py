import os
import csv
import bz2

from django.core.management.base import BaseCommand

from api.models import Disease, Sample, Gene, Mutation


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            dest='path',
            default='data',
            help='Path to location of data files.',
        )

    def handle(self, *args, **options):
        # Diseases
        if Disease.objects.count() == 0:
            print('Loading diseases table...')
            disease_path = os.path.join(options['path'], 'diseases.tsv')
            with open(disease_path) as disease_file:
                disease_reader = csv.DictReader(disease_file, delimiter='\t')
                disease_list = []
                for row in disease_reader:
                    disease = Disease(
                        acronym=row['acronym'],
                        name=row['disease']
                    )
                    disease_list.append(disease)
                Disease.objects.bulk_create(disease_list)

        # Samples
        if Sample.objects.count() == 0:
            print('Loading samples table...')
            sample_path = os.path.join(options['path'], 'samples.tsv')
            with open(sample_path) as sample_file:
                sample_reader = csv.DictReader(sample_file, delimiter='\t')
                sample_list = []
                for row in sample_reader:
                    disease = Disease.objects.get(acronym=row['acronym'])
                    sample = Sample(
                        sample_id=row['sample_id'],
                        disease=disease,
                        gender=row['gender'] or None,
                        age_diagnosed=row['age_diagnosed'] or None
                    )
                    sample_list.append(sample)
                Sample.objects.bulk_create(sample_list)

        # Genes
        if Gene.objects.count() == 0:
            print('Loading genes table...')
            gene_path = os.path.join(options['path'], 'genes.tsv')
            with open(gene_path) as gene_file:
                gene_reader = csv.DictReader(gene_file, delimiter='\t')
                gene_list = []
                for row in gene_reader:
                    gene = Gene(
                        entrez_gene_id=row['entrez_gene_id'],
                        symbol=row['symbol'],
                        description=row['description'],
                        chromosome=row['chromosome'] or None,
                        gene_type=row['gene_type'],
                        synonyms=row['synonyms'].split('|') or None,
                        aliases=row['aliases'].split('|') or None
                    )
                    gene_list.append(gene)
                Gene.objects.bulk_create(gene_list)

        # Mutations
        if Mutation.objects.count() == 0:
            print('Loading mutations table...')
            mutation_path = os.path.join(options['path'], 'mutation-matrix.tsv.bz2')
            with bz2.open(mutation_path , 'rt') as mutation_file:
                mutation_reader = csv.DictReader(mutation_file, delimiter='\t')
                mutation_list = []
                count = 0
                for row in mutation_reader:
                    sample_id = row.pop('sample_id')
                    count += 1
                    if count % 1000 == 0:
                        print('Processing ' + str(count) + ' rows so far')
                    for entrez_gene_id, mutation_status in row.items():
                        if mutation_status == '1':
                            #try:
                                mutation = Mutation(gene_id=entrez_gene_id, sample_id=sample_id)
                                mutation_list.append(mutation)
                            #except:
                            #    print('Had an issue inserting sample', sample_id, 'mutation', entrez_gene_id)
                print('Bulk loading mutation data...')
                Mutation.objects.bulk_create(mutation_list, batch_size=1000)
