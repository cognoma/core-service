# Cognoma API


## Overview

The Cognoma API allows User Interfaces, backend processes, and third parties to access the cognoma application database.

## Schemas

### Task Definition (/task-defs)

| Field        | Type           | Description | Read-Only
| ------------- |:-------------:| ----------:| ----------:|
| name | string | Primary Key. May only contain lowercase alphanumeric charaters, dashes, and underscores. Ex classifier_search. Max 255.| N |
| title | string | The task's display friendly name. Ex "Classifier Search". Max 255. | N |
| description | string | Text describing details of the task. Max 2048. | N |
| default_timeout | integer | The default timeout for the task, in seconds. When a worker has stopped reporting on the task and the task has not completed or failed, the task is given to another worker. Default 600. | N |
| max_attempts | integer | The maxium number of times a task can be attempted. Default 1. | N |
| created_at | datetime | When the task def was created | Y |
| updated_at | datetime | When the task def was last updated | Y |

### Classifier (/classifiers)

A classifier represents a classifier built using machine learning in Cognoma.

| Field        | Type           | Description | Read-Only
| ------------- |:-------------:| ----------:| ----------:|
| id | integer | Primary Key. Auto-incrementing. | Y |
| title | string | Classifier type. May only contain lowercase alphanumeric characters, dashes, and underscores. Ex classifier_search. Max 255.| Y |
| name | string | Name of the classifier. Max 255. | N |
| description | string | Text describing details of the classifier. Max 2048. | N |
| genes | array[integer] | Genes to be used in the classifier. Entrez GeneIDs. Can be expanded. eg ?expand=genes | N |
| diseases | array[string] | Diseases of interest for the classifier. ex ["LUAD","ACC"] Can be expanded. eg ?expand=diseases | N |
| user_id | integer | Foreign Key referencing the user who created the classifier. Can be expanded. eg ?expand=user | Y |
| status | string | The status of the task. Enumeration, options below. Set by service. | Y |
| locked_at | datetime | The last time a worker was issued or touched a task. Set by service. | Y |
| priority | integer | The task's priority. Enumeration, options below. | Y |
| started_at | datetime | When the task was started | Y |
| completed_at | datetime | When the task completed, this is also how a worker communicates success. | Y |
| failed_at | datetime | When the task failed, this is also how a worker communicates failure. | Y |
| attempts | integer | The number of times the task has been attempted so far. Used for retrying. Set by service. | Y |
| created_at | datetime | When the classifier was created | Y |
| updated_at | datetime | When the classifier was last updated | Y |

#### Classifier Status (status)
 - queued - Queued - Task is in the queue.
 - in_progress - In Progress - Task is in progress, being worked on by a worker.
 - failed_retrying - Failed - Retrying - Task failed and is being retried.
 - failed - Failed - Task has failed.
 - completed - Completed - Task has completed.
 
#### Classifier Priorities (priority)
 - 1: Critical
 - 2: High
 - 3: Normal
 - 4: Low

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

Reference table for genes within Cognoma. Entire model is read-only. This table is populated from the data in [`cognoma/genes`](https://github.com/cognoma/genes).

| Field        | Type           | Description |
| ------------- |:-------------:| ----------:|
| entrez_gene_id | integer | The Entrez GeneID which is also used as the primary key |
| symbol | string | The short human-readable identifier |
| description | string | The official full name for the gene |
| gene_type | string | The type of gene |
| synonyms | array[string] | Alternative symbols |
| aliases | array[string] | Alternative descriptions |

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
Creates a classifier

`POST /classifiers`

POST Data

    {
        genes: [7187],
        diseases: ["LUAD", "ACC"]
    }
    
Response

    {
      "id": 1,
      "title": "classifier-search",
      "name": null,
      "description": null,
      "genes": [
        7187
      ],
      "diseases": [
        "ACC",
        "LUAD"
      ],
      "user": 1,
      "notebook_file": null,
      "created_at": "2017-07-12T17:41:51.775850Z",
      "updated_at": "2017-07-12T17:41:51.961160Z",
      "status": "queued",
      "worker_id": null,
      "priority": 3,
      "timeout": 600,
      "attempts": 0,
      "max_attempts": 1,
      "locked_at": null,
      "started_at": null,
      "completed_at": null,
      "failed_at": null
    }
    
### Get a classifier

Get a classifier. Must authenticate as either a worker or the user who created the classifier to access.

`GET /classifiers/23236?expand=user,task,genes,tissues`
    
Response

    {
      "id": 1,
      "title": "classifier-search",
      "name": null,
      "description": null,
      "genes": [
        {
          "entrez_gene_id": 7187,
          "symbol": "TRAF3",
          "description": "TNF receptor associated factor 3",
          "chromosome": "14",
          "gene_type": "protein-coding",
          "synonyms": [
            "CAP-1",
            "CAP1",
            "CD40bp",
            "CRAF1",
            "IIAE5",
            "LAP1"
          ],
          "aliases": [
            "TNF receptor-associated factor 3",
            "CD40 associated protein 1",
            "CD40 binding protein",
            "CD40 receptor associated factor 1",
            "LMP1-associated protein 1"
          ],
          "mutations": [
            41267,
            46092,
            47487,
            61077,
            80675,
            82822,
            183600,
            199561,
            211708,
            240421,
            275613,
            296862,
            364116,
            369000,
            379724,
            384694,
            385207,
            395770,
            440878,
            445597,
            458902,
            468927,
            471347,
            505088,
            542902,
            618628,
            699667,
            736068,
            742720,
            770740,
            774076,
            838474,
            862645,
            871136
          ]
        }
      ],
      "diseases": [
        "ACC",
        "LUAD"
      ],
      "user": {
        "id": 1,
        "name": "Derek Goss",
        "email": "dcgoss14@gmail.com",
        "created_at": "2017-07-12T17:37:21.795286Z",
        "updated_at": "2017-07-12T17:37:21.795335Z"
      },
      "notebook_file": null,
      "created_at": "2017-07-12T17:41:51.775850Z",
      "updated_at": "2017-07-12T17:41:51.961160Z",
      "status": "queued",
      "worker_id": null,
      "priority": 3,
      "timeout": 600,
      "attempts": 0,
      "max_attempts": 1,
      "locked_at": null,
      "started_at": null,
      "completed_at": null,
      "failed_at": null
}
    
