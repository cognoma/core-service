from django.db import connection
from api.models import Classifier

get_classifiers_sql = """
WITH nextClassifiers as (
    SELECT id, started_at, status
    FROM classifiers
    WHERE
       title = ANY(%s)
       AND (status = 'queued' OR
           (status = 'in_progress' AND
            (NOW() > (locked_at + INTERVAL '1 second' * timeout))) OR
           (status = 'failed_retrying' AND
            attempts < max_attempts))
    ORDER BY priority
    FOR UPDATE SKIP LOCKED
    LIMIT %s
)
UPDATE classifiers SET
    status = 'in_progress',
    worker_id = %s,
    locked_at = NOW(),
    started_at =
        CASE WHEN nextClassifiers.started_at = null
             THEN NOW()
             ELSE null
        END,
    attempts =
        CASE WHEN nextClassifiers.status = 'in_progress'
             THEN attempts
             ELSE attempts + 1
        END
FROM nextClassifiers
WHERE classifiers.id = nextClassifiers.id
RETURNING classifiers.*;
"""

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_classifiers(title, worker_id, limit=1):
    with connection.cursor() as cursor:
        cursor.execute(get_classifiers_sql, [title, limit, worker_id])
        raw_classifiers = dictfetchall(cursor)

    classifiers = []
    for raw_classifier in raw_classifiers:
        classifiers.append(Classifier(**raw_classifier))

    return classifiers
