from django.test import TestCase
from .models import TimeChoices
from .models import SkillLevelChoices
from .models import User
from .models import DietaryRestriction
from .models import Recipe
from .models import Ingredients
from .models import RegisteredUser
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from .views import Registered, Recipe_Generator
import json
import os
# Create your tests here.

'''
Some notes:

Django automatically handles the connection to the DB,
When an object is created Django will insert it into the database by itself.
But when I retrive the Item, I retrieve it from the database
'''

class UserTests(TestCase):
    #setup for the model
    def setUp(self):
        #create a user that only has 120 minutes available using the timechoices table
        self.user = User.objects.create(
            available_time = TimeChoices.MIN_90, skill_level = SkillLevelChoices.BEGINNER
            )
        self.user15 = User.objects.create(available_time = TimeChoices.MIN_15)
        
    def test_user_availability(self):
        #check if the created object has the same time available in Timechoices
        self.assertEqual(TimeChoices.MIN_90, self.user.available_time)

        #check other available time
        self.assertEqual(self.user15.available_time, TimeChoices.MIN_15)

    def test_default_user(self):
        # Create a user with default availability and skilllevel
        user = User.objects.create()
        self.assertEqual(user.available_time, TimeChoices.MIN_30)
        self.assertEqual(user.skill_level, SkillLevelChoices.BEGINNER)
    
    def test_user_skills(self):
        #a user with Intermediate skill
        self.assertEqual(self.user.skill_level, SkillLevelChoices.BEGINNER)

class DietaryRestrictionsTest(TestCase):
    def setUp(self):
        #create default user and assign them dietary restrictions object
        self.user = User.objects.create()
        self.user2 = User.objects.create()
        self.restrictions = DietaryRestriction.objects.create(user =self.user, restriction = "restriction1, restriction2")
        self.restrictions.save()
    
    #checks if a user can have more than one restriction (AKA foreign key)
    def test_number_of_restrictions(self):
        # Create another dietary restriction for the same user
        restriction2 = DietaryRestriction.objects.create(user=self.user, restriction="restriction3")
        
        # Get all restrictions the user has
        restrictions = self.user.dietary_restrictions.all()

        self.assertEqual(restrictions.count(), 2)  #test passes becuase user is associated with 2 Dietary objects
        self.assertEqual(self.restrictions.restriction, "restriction1, restriction2") #test if the restrction is the same


    def test_blank_restriction(self):
        restrictions = DietaryRestriction.objects.create(user = self.user2)
        #check if the User can have 0 dietary restrictions
        self.assertEqual("", restrictions.restriction)

class RecipeTest(TestCase):
    def setUp(self):
        self.title = "recipe1"
        self.instruction = "instruction1"
        self.recipe = Recipe.objects.create(title = self.title, instructions = self.instruction)

    #check recipe gets created
    def test_create_recipe(self):
        self.assertIsInstance(self.recipe, Recipe)
        self.assertEqual(self.title, self.recipe.title)
        self.assertEqual(self.instruction, self.recipe.instructions)
        self.assertEqual(TimeChoices.MIN_30, self.recipe.estimated_time)
        self.assertEqual(SkillLevelChoices.BEGINNER, self.recipe.skill_level)

class RegisteredUserTest(TestCase):
    def setUp(self):
        self.rUser = RegisteredUser.objects.create(
            first_name = "Bob",
            last_name = "Joe",
            username = "BJoe",
            email = "bjoe@gmail.com",
            is_admin = False
        )
        self.recipe1 = Recipe.objects.create(title = "recipe1", instructions = "instructions1")
        self.recipe2 = Recipe.objects.create(title = "recipe2", instructions = "instructions2")
        self.recipe3 = Recipe.objects.create(title = "recipe3", instructions = "instructions3")
        self.recipe4 = Recipe.objects.create(title = "recipe4", instructions = "instructions4")
        self.recipe5 = Recipe.objects.create(title = "recipe5", instructions = "instructions5")
        self.recipe6 = Recipe.objects.create(title = "recipe6", instructions = "instructions6")

    def test_add_viewed_recipes(self):
        self.rUser.add_viewed_recipe(self.recipe1)
        self.rUser.add_viewed_recipe(self.recipe2)
        self.rUser.add_viewed_recipe(self.recipe3)
        self.rUser.add_viewed_recipe(self.recipe4)
        self.rUser.add_viewed_recipe(self.recipe5)
        self.rUser.add_viewed_recipe(self.recipe6)
        
        #the 6th recipe should be in last_used_recipe
        self.assertIn(self.recipe6, self.rUser.last_used_recipes.all())
        #the 1st recipe should not be in last_used_recipe
        self.assertNotIn(self.recipe1, self.rUser.last_used_recipes.all())

'''need to use a fake_json file because the sevaed_recipe json will change everytime


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
        self.registered = Registered(name="John Doe",username="jd",phone_number="1234567890",
                                      email_address="jd@gmail.com", password="test",available_time="Anytime")

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

'''

import tempfile
import json
import os

class SaveRecipeTestCase(TestCase):
    def setUp(self):
        # Path to saved_recipe.json
        self.file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saved_recipe.json')

        # Backup existing file
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as original:
                self.original_content = original.read()
        else:
            self.original_content = None

        # Create test JSON content
        test_data = {
            "recipe": {
                "recipe_name": "Simple Tomato Soup",
                "skill_level": "Intermediate",
                "time": "60 minutes",
                "dietary_restrictions": "Vegetarian",
                "ingredients": [
                    {"name": "Tomatoes", "amount": "28", "unit": "oz"},
                    {"name": "Onion", "amount": "1", "unit": "medium"},
                    {"name": "Vegetable Soup", "amount": "32", "unit": "oz"}
                ],
                "steps": [
                    {"step": 1, "instruction": "Dice the onion and sauté in a large pot until translucent."},
                    {"step": 2, "instruction": "Add the tomatoes..."},
                    {"step": 3, "instruction": "Pour in the vegetable soup..."},
                    {"step": 4, "instruction": "Blend and season with salt and pepper."}
                ]
            }
        }

        # Write test JSON to saved_recipe.json
        with open(self.file_path, 'w') as f:
            json.dump(test_data, f)

        # Create mock registered user
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd",
            email="jd@gmail.com",
            hashed_password=make_password("test")
        )

        self.registered = Registered(name="John Doe", username="jd", phone_number="1234567890",
                                     email_address="jd@gmail.com", password="test", available_time="Anytime")

    def tearDown(self):
        # Restore the original saved_recipe.json
        if self.original_content is not None:
            with open(self.file_path, 'w') as f:
                f.write(self.original_content)
        else:
            os.remove(self.file_path)

    def test_save_recipe(self):
        self.registered.save_recipe()

        # Assert the recipe was saved
        recipe = Recipe.objects.get(title="Simple Tomato Soup")
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.skill_level, SkillLevelChoices.INTERMEDIATE)

        # Assert ingredients were saved
        ingredients = Ingredients.objects.filter(recipe=recipe)
        self.assertEqual(len(ingredients), 3)
        self.assertEqual(ingredients[0].ingredient, "Tomatoes")
        self.assertEqual(ingredients[1].ingredient, "Onion")
        self.assertEqual(ingredients[2].ingredient, "Vegetable Soup")

'''Testing API calls'''
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient,RequestsClient
import json


class TestApiCalls(TestCase):
    def setUp(self):
        self.client = APIClient()
   

    def test_post_to_gen_recipe(self):
        data = {
            'ingredients': ['onion', 'tomato', 'celery'],
            'skill_level': "Beginner",
            'dietary_restrictions': [],
            'time': "60 minutes"
        }
        response = self.client.post('/generate_recipe/', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_incorrect_post_to_gen_recipe(self):
        data = {
            'ingredients': ['onion', 'tomato', 'celery'],
            'dietary_restrictions': [],
            'time': "60 minutes"
        }
        response = self.client.post('/generate_recipe/', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)

