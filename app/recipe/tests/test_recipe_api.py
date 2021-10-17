from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import serializers, status
import rest_framework
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    '''return recipe detail url'''
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Main Course'):
    '''create and return sample tag'''
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='salt'):
    '''create and return a sample ingredient'''
    return Ingredient.objects.create(user=user, name=name)

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

    
    def test_view_recipe_details(self):
        '''test viewing a recipe details'''
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        '''Test creating recipe'''
        payload = {
            'title' : 'Chocolate Cheesecake',
            'time_minutes' : 10,
            'price' : 6.00
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        '''test creating recipes with tags'''
        tag1 = sample_tag(user = self.user, name='tag1')
        tag2 = sample_tag(user = self.user, name='tag2')
        payload = {
            'title': 'Title1',
            'time_minutes': 10,
            'price': 5.00,
            'tags' : [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)


    def test_create_recipe_with_ingredients(self):
        '''test create recipe with ingredients'''
        ingredient1 = sample_ingredient(user= self.user, name= 'Ind1')
        ingredient2 = sample_ingredient(user= self.user, name= 'Ind2')
        payload = {
            'title' : 'Title1',
            'time_minutes' : 10,
            'price' : 5.00,
            'ingredients' : [ingredient1.id, ingredient2.id]
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
