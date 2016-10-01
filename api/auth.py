from rest_framework import authentication, permissions
from rest_framework import exceptions

from api.models import User

class CognomaAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return None

        auth_header = request.META['HTTP_AUTHORIZATION']

        print(auth_header)

        if not auth_header:
            return None

        token = str.replace(auth_header, "Bearer ", "")

        try:
            user = User.objects.get(random_slugs__contains=[token])
            print(user.id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        return (user, None)

    def authenticate_header(self, request):
        return "HTTP 401 Unauthorized"
