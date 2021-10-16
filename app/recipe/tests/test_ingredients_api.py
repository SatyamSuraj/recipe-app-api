from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import ignore_warnings
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTests(TestCase):
    '''test the publicily available api'''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''test that login is required to access the endpioint'''
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    '''test the private available api'''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'test@123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        '''Test retriving a list of ingredients'''
        Ingredient.objects.create(user=self.user, name='sugar')
        Ingredient.objects.create(user=self.user, name='salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_to_limited_user(self):
        '''Test the ingredient for the authenticated user are returned'''
        user2 = get_user_model().objects.create_user(
            'test_2@test.com',
            'test2@123'
        )
        Ingredient.objects.create(user=user2, name='Viniger')

        ingredient = Ingredient.objects.create(user=self.user, name='Turmeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        '''Test create a new ingredient'''
        payload = {'name':'Cabbage'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        '''Test create ingredient creation failure'''
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)