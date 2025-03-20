from django.test import TestCase
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from .models import RegisteredUser, Recipe, Ingredients, Token, SkillLevelChoices  # import your models
from .views import Registered
from .profile_manager import profileManager
from authentication import Authenticator
from recipe_manager import RecipeManager
import json
import os
from datetime import datetime, timedelta
from django.utils import timezone
import uuid

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





class UpdateProfileTest(TestCase):
    def setUp(self):
        # Create a mock registered user
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd1",
            email="jd1@gmail.com",
            hashed_password=make_password("testing1")
        )
        
        self.token = Token.objects.create(
            user=self.user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # Instantiate the Registered user class from your code
        self.profile_manager = profileManager(self=self.user)

    def test_update_profile(self):
        new_data = {
            "skill_level": SkillLevelChoices.INTERMEDIATE,
            "dietary_restrictions": {"Beef"}
        }
            
        response, status_code = self.profile_manager.update_profile(self.token.token, new_data)
        
        self.assertEqual (status_code, 200)
        self.assertEqual(response,{"success": "Profile updated successfully"})
        
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.skill_level, SkillLevelChoices.INTERMEDIATE)
        
        dietary_restrictions = list(self.user.dietary_restrictions.value_list("restriction",  flat=True))
        self.assertEqual(len(dietary_restrictions), 1)
        self.assertEqual("Beef", dietary_restrictions)


class LoginTest(TestCase):
    def setUp(self):
        # Create a mock registered user
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd2",
            email="jd2@gmail.com",
            hashed_password=make_password("testing1")
        )

    def test_successful_login(self):
        authenticator = Authenticator(email_address="jd2@gmail.com", password="testing1")

        response, status_code = authenticator.sign_in()

        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], f"Welcome back, {self.user.first_name}!")

        token = Token.objects.filter(user=self.user).first()
        self.assertIsNotNone(token)
        self.assertTrue(token.is_valid())


        self.assertEqual(response["user_id"], self.user.id)
        self.assertEqual(response["first_name"], self.user.first_name)
        self.assertEqual(response["last_name"], self.user.last_name)
        self.assertEqual(response["username"], self.user.username)
        self.assertEqual(response["email"], self.user.email)
        self.assertEqual(response["skill_level"], self.user.skill_level)
        self.assertEqual(response["dietary_restrictions"], list(self.user.dietary_restrictions.values_list("restriction", flat=True)))

        self.assertIn("access", response)
        self.assertIn("refresh", response)
        
        
        
class SignUpTest(TestCase):
    def test_working_sign_up(self):
        # Create a mock registered user
        
        new_user_data = {
            "first_name" : "Jane",
            "last_name" : "Doe",
            "username" : "jane_doe",
            "email" : "jane.doe@gmail.com",
            "password" : "testing1"
        }
        
        authenticator = Authenticator()
        response, status_code = authenticator.sign_up(new_user_data)
        
        self.assertEqual(status_code, 201)
        self.assertEqual(response["message"], f"User {new_user_data['username']} successfully registered")
        
        user = RegisteredUser.objects.filter(username=new_user_data["username"]).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, new_user_data["first_name"])
        self.assertEqual(user.last_name, new_user_data["last_name"])
        self.assertEqual(user.email, new_user_data["email"].strip().lower())
        self.assertTrue(user.check_password(new_user_data["password"]))
        
        


class LogoutTest(TestCase):
    def setUp(self):
        # Create a mock registered user
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd2",
            email="jd2@gmail.com",
            hashed_password=make_password("testing1")
        )
        
        self.token = Token.objects.create(
            user=self.user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(minutes=10)
        )

    def test_logout(self):
        authenticator = Authenticator()
        
        response, status_code = authenticator.logout(self.token.token)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["message"], "Logged out successfully")
        
        token_exists = Token.objects.filter(token=self.token.token).exists()
        self.assertFalse(token_exists)