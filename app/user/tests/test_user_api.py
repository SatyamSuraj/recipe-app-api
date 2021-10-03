from django.forms.fields import EmailField
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.fields import empty

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    '''Test user API public'''    

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        '''Test create user with valid payload is successfull'''
        payload = {
            'email': 'test@test.com',
            'password': 'test@123',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_user_exists(self):
        '''Test if user already exist'''
        payload = {
            'email': 'test@test.com',
            'password': 'test@123',
            'name': 'Test Name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''Test that the password must be more than 5 char'''

        payload = {'email': 'test@test.com', 'password': 'test', 'name': 'test_name'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''Test that a token is created for the user'''
        payload = {'email': 'test@test.com', 'password': 'test_pass', 'name': 'test_name'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_create_token_invalid_credentials(self):
        '''Test that token is not created if invalid credentials are given'''
        create_user(email='test@test.com', password='test_pass', name='test_name')
        payload = {'email': 'test@test.com', 'password': 'test@123', 'name': 'test_name'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        '''Test that token is not created if user does not exist'''
        payload = {'email': 'test@test.com', 'password': 'test_pass', 'name': 'test_name'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        '''Test that email and password and name is required'''
        res = self.client.post(TOKEN_URL, {'email': 'test@test.com', 'password': '', 'name': 'test_name'})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)