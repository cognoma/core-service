# Cognoma API


## Overview

The Cognoma API allows User Interfaces, backend processes, and third parties to access the cognoma application database.

## Schemas

### Classifier (/classifiers)

A classifier represents a classifer built using machine learning in Cognoma.


| Field        | Type           | Description | Read-Only
| ------------- |:-------------:| ----------:| ----------:|
| id | integer | Primary Key. Auto-incrementing. | Y |
| algorithm | string | Foreign Key referencing the machine learning algorithm was used to produce the classifier. | N |
| algorithm_parameters | object | Algorithm specific parameters. Stored as JSONB in Postgres. | N |
| genes | array[integer] | Genes to be used in the classifer. entrezids. Can be expanded. eg ?expand=genes | N |
| tissues | array[string] | Tissues of interest for the classifer. ex ["KIRC","KIRP"] Can be expanded. eg ?expand=tissues | N |
| user_id | integer | Foreign Key referencing the user who created the classifer. Can be expanded. eg ?expand=user | Y |
| task_id | integer |  Foreign Key referencing the classifier task. Can be expanded. eg ?expand=user,task | Y |
| results | object | Results for the machine learning classifer. Stored as JSONB in Postgres. | N |
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

### Algorithm (/algorithms)

Machine learning algorithms available in Cognoma.


| Field        | Type           | Description | Read-Only
| ------------- |:-------------:| ----------:| ----------:|
| name | string | Primary Key. | Y |
| parameters | object | JSON Schema used to generate algorithm parameter forms and displays. | Y |

### Gene (/genes)

Reference table for genes within Cognoma. Entire model is read-only.


| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| entrezid | integer | Primary Key. |
| systematic_name | string |  |
| standard_name | string |  |
| description | string |  |
| organism | integer | Foreign Key referencing the Organism. |
| aliases | string |  |
| obsolete | boolean |  |
| weight | boolean |  |
| sample_mutation_sumary | object | Count/aggregates of sample mutations available in Cognoma for this particular gene. |

#### Tissues (/tissues)

Entire model is read-only.

| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| acronym | string | Primary Key. Ex "GBM" |
| name | string | Full tissue name. Ex "Glioblastoma Multiforme" |

### Organism (/organisms)

Reference table for organisms within Cognoma. Entire model is read-only.


| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| taxonomy_id | integer | Primary Key. Taxonomy ID assigned by NCBI. |
| common_name | string | Organism common name, e.g. 'Human' |
| scientific_name | string | Organism scientific/binomial name, e.g. 'Homo sapiens' |

### Sample Mutation Summary (embedded in Gene)

Count/aggregates of sample mutations available in Cognoma for a particular gene. Entire model is read-only.

| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| count | integer | Number of mutations. |

### Sample (/samples)

Select data from the TCGA database used for reference within Cognoma. Entire model is read-only.


| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| tcga_id | string | Primary Key. Sample ID assigned by TCGA. |
| mutations | object | Gene mutation data. |

### Mutation (embedded in Sample)

Sample to gene mutations.

| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| mutation_type | string |  |
| gene | object | Gene associated with this mutation. |

## Example Requests

### Create a classifier

Creates a classifer which creates a task in the task queue.

`POST /classifiers`

POST Data

    {
        algorithm: "svg",
        algorithm_parameters: {
            foo: "bar",
            threshold: 2.3,
            ...
        },
        genes: [7157],
        tissues: ["KIRC","KIRP"]
    }
    
Response

    {
        id: 23236,
        algorithm: "svg",
        algorithm_parameters: {
            foo: "bar",
            threshold: 2.3,
            ...
        },
        genes: [7157],
        tissues: ["KIRC","KIRP"],
        user_id: 2343,
        task_id: 23222,
        results: {},
        created_at: "2016-08-11T03:01:05+00:00",
        updated_at: "2016-08-11T03:01:05+00:00"
    }
    
### Get a classifier

Creates a classifer which creates a task in the task queue.

`GET /classifiers/23236?expand=user,task,genes,tissues`
    
Response

    {
        id: 23236,
        algorithm: "svg",
        algorithm_parameters: {
            foo: "bar",
            threshold: 2.3,
            ...
        },
        genes: [
            {
                entrezid: 7157,
                ...
            },
            ...
        ],
        tissues: [
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
    
