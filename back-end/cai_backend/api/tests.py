from django.test import TestCase
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from .models import RegisteredUser, Recipe, Ingredients  # import your models
from .views import Registered
import json
import os

class SaveRecipeTestCase(TestCase):
    def setUp(self):
        # Create a mock registered user
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd",
            email="jd@gmail.com",
            hashed_password=make_password("test")
        )

        # Instantiate the Registered user class from your code
        self.registered = Registered(name="John Doe",username="jd",phone_number="1234567890", email_address="jd@gmail.com", password="test",available_time="Anytime")

    def test_save_recipe(self):

        self.registered.save_recipe()

        # Assert the recipe was saved
        recipe = Recipe.objects.get(title ="Quick Tomato Onion Sauce")
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.skill_level, "Advanced")

        # Assert ingredients were saved
        ingredients = Ingredients.objects.filter(recipe=recipe)
        self.assertEqual(len(ingredients), 2)
        self.assertEqual(ingredients[0].ingredient, "tomato")
        self.assertEqual(ingredients[1].ingredient, "onion")


