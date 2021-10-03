from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    '''Serializer object for user object'''

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validation_data):
        '''Create a new user with encrypted password and return it'''
        return get_user_model().objects.create_user(**validation_data)


class AuthTokenSerialzer(serializers.Serializer):
    '''Serializer for the user authentication object'''
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )


    def validate(self, attrs):
        '''Validate and authenticate the user'''
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = ('Unable to authenticate with provided creadentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs

