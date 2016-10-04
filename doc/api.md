# Cognoma API


## Overview

The Cognoma API allows User Interfaces, backend processes, and third parties to access the cognoma application database.

## Schemas

### Classifier (/classifiers)

A classifier represents a classifier built using machine learning in Cognoma.

| Field        | Type           | Description | Read-Only
| ------------- |:-------------:| ----------:| ----------:|
| id | integer | Primary Key. Auto-incrementing. | Y |
| genes | array[integer] | Genes to be used in the classifier. entrezids. Can be expanded. eg ?expand=genes | N |
| diseases | array[string] | Diseases of interest for the classifier. ex ["KIRC","KIRP"] Can be expanded. eg ?expand=diseases | N |
| user_id | integer | Foreign Key referencing the user who created the classifier. Can be expanded. eg ?expand=user | Y |
| task_id | integer |  Foreign Key referencing the classifier task. Can be expanded. eg ?expand=user,task | Y |
| results | object | Results for the machine learning classifier. Stored as JSONB in Postgres. | N |
| created_at | datetime | When the classifier was created | Y |
| updated_at | datetime | When the classifier was last updated | Y |

### User (/users)

A user of the Cognoma system.

| Field        | Type           | Description | Read-Only
| ------------- |:-------------:| ----------:| ----------:|
| id | integer | Primary Key. Auto-incrementing. | Y |
| random_slugs | array[string] | Random IDs used by the user to login. | N |
| name | string | Optional name, nickname, or handle the users wants for display purposes. | N |
| email | string | Optional email if the user wishes to get notifications | N |
| last_login | datetime | Last time the user logged in. | Y |

### Gene (/genes)

Reference table for genes within Cognoma. Entire model is read-only. This table is created using [`django-genes`](https://bitbucket.org/greenelab/django-genes).

| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| entrezid | integer | Primary Key. |
| systematic_name | string |  |
| standard_name | string |  |
| description | string |  |
| organism | integer | Foreign Key referencing the Organism. |
| aliases | string | space-separated list of aliases |
| obsolete | boolean |  |
| weight | boolean | Weight used for search results since multiple genes may have the same symbol |

### Organism (/organisms)

Reference table for organisms within Cognoma. Entire model is read-only. This table is created using [`django-organisms`](https://bitbucket.org/greenelab/django-organisms). Note that Project Cognoma will deal exclusively with human genes (when taxonomy_id equals 9606).

| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| taxonomy_id | integer | Primary Key. Taxonomy ID assigned by NCBI. |
| common_name | string | Organism common name, e.g. 'Human' |
| scientific_name | string | Organism scientific/binomial name, e.g. 'Homo sapiens' |

### Disease (/diseases)

Entire model is read-only.

| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| acronym | string | Primary Key. Ex "GBM" |
| name | string | Full tissue name. Ex "Glioblastoma Multiforme" |

### Sample (/samples)

Select data from the TCGA database used for reference within Cognoma. Entire model is read-only.

| Field        | Type          | Description |
| ------------ |:-------------:| ----------:|
| sample_id | string | Primary Key. Sample ID assigned by TCGA. |
| disease | string | Foreign key referencing the disease |
| gender | string | male or female |
| age_diagnosed | integer | patient age when cancer was diagnosed |

### Mutation (embedded in Sample)

Sample to gene mutations.

| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| sample_id | string | Foreign Key referencing samples |
| entrez_gene_id | object | Foreign Key referencing a mutated gene for the sample |

## Example Requests

### Create a classifier

Creates a classifier which creates a task in the task queue.

`POST /classifiers`

POST Data

    {
        mutated_genes: [7157],
        diseases: ["KIRC", "KIRP"]
    }
    
Response

    {
        id: 23236,
        genes: [7157],
        tissues: ["KIRC","KIRP"],
        user_id: 2343,
        task_id: 23222,
        results: {},
        created_at: "2016-08-11T03:01:05+00:00",
        updated_at: "2016-08-11T03:01:05+00:00"
    }
    
### Get a classifier

Get a classifier which has completed the task queue.

`GET /classifiers/23236?expand=user,task,genes,tissues`
    
Response

    {
        id: 23236,
        mutated_genes: [
            {
                entrez_gene_id: 7157,
                ...
            },
            ...
        ],
        diseases: [
        	  {
                acronym: "KIRC",
                name: "Kidney Clear Cell Carcinoma"
            },
            {
                acronym: "KIRP",
                name: "Kidney Papillary Cell Carcinoma"
            }
        ],
        user: {
            id: 2343,
            random_slugs: ["ahgcgf577sj784"],
            name: "awm33",
            email: null,
            last_login: "2016-08-11T03:01:05+00:00"
        },
        task: {
            id: 23222,
            task_def: "classifier_search",
            status: "in_progress",
            received_at: "2016-08-11T03:01:05+00:00",
            priority: "normal",
            unique: "user-23222-classifier-23236",
            data: {
               ...
            },
            run_at: "2016-08-11T03:01:05+00:00",
            attempts: 1
        },
        results: {
            ...
        },
        created_at: "2016-08-11T03:01:05+00:00",
        updated_at: "2016-08-11T03:01:05+00:00"
    }
    
