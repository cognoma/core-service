import re

from rest_framework import authentication, permissions
from rest_framework import exceptions
from django.conf import settings
import jwt

from api.models import User

class CognomaAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return None

        auth_header = request.META['HTTP_AUTHORIZATION']

        if not auth_header:
            return None

        match = re.match("^(?P<type>Bearer|JWT)\s(?P<token>.+)$", auth_header)

        if not match:
            return None

        auth_type = match.group('type')
        token = match.group('token')

        if auth_type == 'Bearer':
            try:
                user = User.objects.get(random_slugs__contains=[token])
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not found')

            return (user, {'type': auth_type})
        elif auth_type == 'JWT':
            try:
                payload = jwt.decode(token, settings.JWT_PUB_KEY, algorithms=["RS256"])
            except:
                return None

            if 'service' not in payload:
                return None

            service = payload['service']

            return (service, {'type': auth_type, 'service': service})
        else:
            return None

    def authenticate_header(self, request):
        return "HTTP 401 Unauthorized"

class UserUpdateSelfOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != 'PUT' and request.method != 'PATCH':
            return True

        if not request.user:
            raise exceptions.NotAuthenticated()

        if request.auth['type'] == 'JWT' or request.user.id == obj.id:
            return True

        return False

class IsAuthenticatedOrReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user:
            raise exceptions.NotAuthenticated()
        else:
            return True

class ClassifierRetrievePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user:
            return False
        elif request.auth['type'] == 'JWT' and request.auth['service'] == 'core':
            return True
        else:
            return obj.user == request.user

class MLWorkerOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            raise exceptions.NotAuthenticated()
        elif request.auth['type'] == 'JWT' and request.auth['service'] == 'core':
            return True
        else:
            raise exceptions.NotAuthenticated()
