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
        self.registered = Registered(self.user)

    def test_save_recipe(self):
        # Call the save_recipe method
        self.registered.save_recipe()

        # Assert the recipe was saved
        recipe = Recipe.objects.get(recipe_name="Quick Tomato Onion Sauce")
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.skill_level, "Advanced")

        # Assert ingredients were saved
        ingredients = Ingredients.objects.filter(recipe=recipe)
        self.assertEqual(len(ingredients), 2)
        self.assertEqual(ingredients[0].ingredient_name, "tomato")
        self.assertEqual(ingredients[1].ingredient_name, "onion")


