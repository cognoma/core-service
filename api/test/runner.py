from types import MethodType
from django.test.runner import DiscoverRunner
from django.db import connections

def prepare_database(self):
    self.connect()
    self.connection.cursor().execute("""
    CREATE SCHEMA cognoma AUTHORIZATION app;
    GRANT ALL ON SCHEMA cognoma TO app;
    """)

class PostgresSchemaTestRunner(DiscoverRunner):
    """
    Because testing creates/destroys a new database each time, we have to setup
    schema level permissions each time as well.

    This class is based on http://stackoverflow.com/a/37861814
    """

    def setup_databases(self, **kwargs):
        for connection_name in connections:
            connection = connections[connection_name]
            connection.prepare_database = MethodType(prepare_database, connection)
        return super().setup_databases(**kwargs)
