from django.shortcuts import render
from rest_framework_mongoengine import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import get_authorization_header

from gears.serializers import GearSerializer
from gears.models import Gear
from accounts.authentication import TokenAuthentication
from accounts.models import Token
from permissions import IsOwnerOrReadOnly


class GearViewSet(viewsets.ModelViewSet):
    """ methods for Gears
    only editable and creatable when authenticated """

    # make writable only if authenticated
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)

    lookup_field = 'gear'
    serializer_class = GearSerializer
    queryset = Gear.objects.all()

    def create(self, request):
        """Acquire the token, looks for its referenced
        'user' then save the referenced user in 'owner' field
        of Gear model
        """
        # acquire the token given
        received_token = get_authorization_header(self.request).split()
        # acquire the stored token using the key of token that was provided
        stored_token = Token.objects.get(key=received_token[1].decode())
        
        # add 'owner' to the POST body using the user id stored in the Token
        request.data['owner'] = stored_token.user.id
        serializer = self.serializer_class(data=request.data, 
                                            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response('Gear created!', status=status.HTTP_201_CREATED)