from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerialzer


class CreateUserView(generics.CreateAPIView):
    '''Create new user in the system'''
    serializer_class = UserSerializer
 

class CreateTokenView(ObtainAuthToken):
    '''create a new auth token for a user'''
    serializer_class = AuthTokenSerialzer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
