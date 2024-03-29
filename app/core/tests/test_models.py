from unittest.mock import patch  

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email='test@test.com', password='test@123'):
    '''create a sample user'''
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    
    def test_create_user_with_email_successful(self):
        '''Test creating user with email is success'''
        email = 'test@gamil.com'
        password = 'Test@123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normalized(self):
        '''Test the email for a new user is normalized'''
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user( email, "test@123")

        self.assertEqual(user.email, email.lower())


    def test_new_user_email(self):
        '''Test user creation with no email address'''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test@123")    


    def test_create_new_super_user(self):
        '''Test creating spuer user'''

        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test@123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    def test_tag_str(self):
        '''Test the tag string representation'''
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)


    def test_ingredient_str(self):
        '''Test the inredient string representation'''
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)


    def test_recipe_str(self):
        '''test the recipe string representation'''
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title = 'Butter Panner',
            time_minutes  = 5,
            price = 5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        '''test image is saved in correct location'''
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
         