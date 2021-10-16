from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import serializers, status
import rest_framework
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    '''create and return sample recipe'''
    defaults = {
        'title': 'Sample title',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)
     
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):
    '''test unauthetictaed recipe api access'''

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        '''test that auth is required'''
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    '''Test authenticated recipe api'''

    def setUp(self):
        self.client = APIClient(); 
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'test@123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        '''Test retrieving a list of recipe'''
        sample_recipe(user = self.user)
        sample_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_recipes_limited_to_user(self):
        '''test retrieving recipe for user'''
        user2 = get_user_model().objects.create_user(
            'test_1@test.com',
            'test@123434'
        )

        sample_recipe(user = user2)
        sample_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data), 1)
        self.assertTrue(res.data, serializer.data)