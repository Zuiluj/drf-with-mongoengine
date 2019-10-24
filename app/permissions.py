from rest_framework import permissions
from rest_framework.authentication import get_authorization_header

from accounts.models import Token

class IsOwnerOrReadOnly(permissions.BasePermission):
    """ Custom permissions to allow anonymous to view but not edit and delete """

    def has_object_permission(self, request, view, obj):
        # allow GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # receive the token as an array
        post_token = get_authorization_header(request).split()
        # get the second element of the array, which is the Token's key itself
        current_user = Token.objects.key(key=post_token[1])
        return obj.owner == current_user # compare gear's owner id to current logged in user's id