from rest_framework import authentication, permissions
from rest_framework import exceptions

from api.models import User

class CognomaAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return None

        auth_header = request.META['HTTP_AUTHORIZATION']

        if not auth_header:
            return None

        token = str.replace(auth_header, "Bearer ", "")

        try:
            user = User.objects.get(random_slugs__contains=[token])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        return (user, None)

    def authenticate_header(self, request):
        return "HTTP 401 Unauthorized"

class UserUpdateSelfOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != 'PUT':
            return True

        if not request.user:
            raise exceptions.NotAuthenticated()

        if request.user.id == obj.id:
            return True

        return False

class ClassifierPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user:
            raise exceptions.NotAuthenticated()

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user:
            raise exceptions.NotAuthenticated()

        if request.user.id == obj.user.id:
            return True

        return False
