from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.utils.field_mapping import get_relation_kwargs
from user.serializers import UserSerializer, AuthTokenSerialzer


class CreateUserView(generics.CreateAPIView):
    '''Create new user in the system'''
    serializer_class = UserSerializer
 

class CreateTokenView(ObtainAuthToken):
    '''create a new auth token for a user'''
    serializer_class = AuthTokenSerialzer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    '''Manage authenticated user'''
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


    def get_object(self):
        '''Reterieve and return authenticated user'''
        return self.request.user