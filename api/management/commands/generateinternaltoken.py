import os
from datetime import datetime

from django.core.management.base import BaseCommand
import jwt

class Command(BaseCommand):
    help = 'Generates a JWT for use internally inside Cognoma.'

    def add_arguments(self, parser):
        parser.add_argument('service', nargs='+', type=str, help='Internal service name, ex "task"')
        parser.add_argument('private_key_file', nargs='+', type=str, help='Path to RSA private key')
        parser.add_argument('issuer', nargs='+', type=str, help='Issuer (you) Github handle')

    def handle(self, *args, **options):
        service = options['service'][0]
        issuer = options['issuer'][0]

        print('Creating token for service "' +
              service +
              '", issued by "' +
              issuer +
              '"')

        private_key = open(options['private_key_file'][0]).read()

        token = jwt.encode({
                                'service': service,
                                'iat': datetime.utcnow(),
                                'iss': issuer
                            },
                           private_key,
                           algorithm="RS256")

        print(token.decode())
