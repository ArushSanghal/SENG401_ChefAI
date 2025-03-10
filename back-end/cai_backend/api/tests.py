from django.test import TestCase
from .models import TimeChoices
from .models import SkillLevelChoices
from .models import User
from .models import DietaryRestriction
from .models import Recipe
from .models import Ingredients
from .models import RegisteredUser

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
