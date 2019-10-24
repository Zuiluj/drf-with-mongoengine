import json
import logging

from django.utils import timezone
from django.shortcuts import render
from rest_framework import views, mixins, permissions, exceptions, generics
from rest_framework import status
from rest_framework_mongoengine import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.views import ObtainAuthToken

from accounts.serializers import UserSerializer, AuthTokenSerializer
from accounts.models import User, Token
from accounts.authentication import TokenAuthentication
from permissions import IsOwnerOrReadOnly


class CreateUser(mixins.CreateModelMixin, 
                generics.GenericAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    
class UpdateUser(mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                generics.GenericAPIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)

    lookup_field = 'username'
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        obj = User.objects.get(username=self.kwargs.get('username'))
        serializer = self.serializer_class(data=obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        obj = User.objects.get(username=self.kwargs.get('username'))
        serializer = UserSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'update': 'successful'
        }, status=status.HTTP_200_OK)

class AuthToken(views.APIView):
    """Custom Token acquire view
    
    Serialize first if it's valid, then if True, it will acquire/create a
    new token specifically to the user.
    """
    # initialize auth classes to none as this should be a view where
    # you will acquire an auth token, thus, no auth is required
    authentication_classes = ()
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
        
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # check first if the token is still valid, if not --
        # delete it then create new
        try:
            token = Token.objects.get(user=user)
            if (timezone.now().replace(tzinfo=None) - token.created).total_seconds() > 86400:
                token.delete()
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)

        return Response({
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class Logout(views.APIView):
    """Logs out the user and flush the token to nowhere"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
        
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        Token.objects.get(user=user).delete()
        return Response('User logged out, Token was flushed in the toilet.', status=status.HTTP_200_OK)