from django.utils import timezone, timesince
from rest_framework import status, exceptions
from rest_framework.authentication import get_authorization_header, BaseAuthentication

from accounts.models import Token

class TokenAuthentication(BaseAuthentication):
    
    def get_model(self):
        return Token

    def authenticate(self, request):
        """Authenticate the request header and see if it has the token and also if it's valid."""
        # acquire headers and split it to enable operations
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        # token must not contain special characters
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        """Authenticate the credentials in POST body"""
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        # check if the the token lasted more than 24 hours
        if (timezone.now().replace(tzinfo=None) - token.created).total_seconds() > 86400:
            raise exceptions.AuthenticationFailed('Token already expired. Kindly login to refresh your token.')
            
        return (token.user, token)