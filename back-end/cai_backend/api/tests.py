from django.test import TestCase
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from .models import RegisteredUser, Recipe, Ingredients, Token, SkillLevelChoices
# from .views import Registered
from .services.profile_manager import ProfileManager
from .services.authenticator import Authenticator
from .services.save_manager import SaveManager
from .services.recipe_parser import RecipeParser
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
from django.http.response import JsonResponse
import tempfile
import os
import json
from rest_framework_simplejwt.tokens import AccessToken


# All tests passed
class UpdateProfileTest(TestCase):
    def setUp(self):
        # Create a mock registered user
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd5",
            email="jd5@gmail.com",
            hashed_password=make_password("testing1")
        )
        
        self.token = AccessToken.for_user(self.user)

        # Instantiate the Registered user class from your code
        self.profile_manager = ProfileManager(self.user)

    def test_update_profile(self):
        new_data = {
            "skill_level": SkillLevelChoices.INTERMEDIATE,
            "dietary_restrictions": {"Beef"}
        }
            
        response, status_code = self.profile_manager.update_profile(str(self.token), new_data)
        
        self.assertEqual (status_code, 200)
        self.assertEqual(response,{"success": "Profile updated successfully"})
        
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.skill_level, SkillLevelChoices.INTERMEDIATE)
        
        dietary_restrictions = list(self.user.dietary_restrictions.values_list("restriction",  flat=True)) # type: ignore
        self.assertEqual(len(dietary_restrictions), 1)
        self.assertEqual(['Beef'], dietary_restrictions)
        
    def test_update_profile_skill_level_only(self):
        new_data = {
            "skill_level": SkillLevelChoices.ADVANCED
        }
            
        response, status_code = self.profile_manager.update_profile(str(self.token), new_data)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"success": "Profile updated successfully"})
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.skill_level, SkillLevelChoices.ADVANCED)

    def test_update_profile_dietary_restrictions_only(self):
        new_data = {
            "dietary_restrictions": {"Beef", "Milk"}
        }
            
        response, status_code = self.profile_manager.update_profile(str(self.token), new_data)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"success": "Profile updated successfully"})
        
        self.user.refresh_from_db()
        dietary_restrictions = list(self.user.dietary_restrictions.values_list("restriction", flat=True)) # type: ignore
        self.assertEqual(len(dietary_restrictions), 2)
        self.assertIn('Beef', dietary_restrictions)
        self.assertIn('Milk', dietary_restrictions)
    
    def test_update_profile_empty_dietary_restrictions(self):
        new_data = {
            "dietary_restrictions": []
        }
            
        response, status_code = self.profile_manager.update_profile(str(self.token), new_data)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"success": "Profile updated successfully"})
        
        self.user.refresh_from_db()
        dietary_restrictions = list(self.user.dietary_restrictions.values_list("restriction", flat=True)) # type: ignore
        self.assertEqual(len(dietary_restrictions), 0)
    
    def test_update_profile_invalid_token(self):
        response, status_code = self.profile_manager.update_profile("invalid_token", {"skill_level": SkillLevelChoices.INTERMEDIATE})
        self.assertEqual(status_code, 401)
        self.assertEqual(response["error"], "Invalid token")
        

# All tests passed
class GetUserDataTest(TestCase):
    def setUp(self):
        # Create a mock registered user
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd1",
            email="jd1@gmail.com",
            hashed_password=make_password("testing1")
        )
        
        # Create a valid token for the user
        self.valid_token = Token.objects.create(
            user=self.user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # Create an expired token for the user
        self.expired_token = Token.objects.create(
            user=self.user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() - timedelta(minutes=10)
        )

        # Instantiate the ProfileManager
        self.profile_manager = ProfileManager(self.user)

    def test_get_user_data_valid_token(self):
        response, status_code = self.profile_manager.get_user_data(self.valid_token.token)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["user_id"], self.user.pk)
        self.assertEqual(response["first_name"], self.user.first_name)
        self.assertEqual(response["last_name"], self.user.last_name)
        self.assertEqual(response["username"], self.user.username)
        self.assertEqual(response["email"], self.user.email)
        self.assertEqual(response["skill_level"], self.user.skill_level)
        self.assertEqual(response["dietary_restrictions"], list(self.user.dietary_restrictions.values_list("restriction", flat=True))) # type: ignore

    def test_get_user_data_invalid_token(self):
        response, status_code = self.profile_manager.get_user_data("invalid_token")
        
        self.assertEqual(status_code, 401)
        self.assertEqual(response["error"], "Invalid or expired token")

    def test_get_user_data_expired_token(self):
        response, status_code = self.profile_manager.get_user_data(self.expired_token.token)
        
        self.assertEqual(status_code, 401)
        self.assertEqual(response["error"], "Invalid or expired token")


# All tests passed
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


        self.assertEqual(response["user_id"], self.user.pk)
        self.assertEqual(response["first_name"], self.user.first_name)
        self.assertEqual(response["last_name"], self.user.last_name)
        self.assertEqual(response["username"], self.user.username)
        self.assertEqual(response["email"], self.user.email)
        self.assertEqual(response["skill_level"], self.user.skill_level)
        self.assertEqual(response["dietary_restrictions"], list(self.user.dietary_restrictions.values_list("restriction", flat=True))) # type: ignore

        self.assertIn("access", response)
        self.assertIn("refresh", response)
        

# All tests passed
class LoginEdgeCaseTest(TestCase):
    def setUp(self):
        # Create a mock registered user
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd2",
            email="jd2@gmail.com",
            hashed_password=make_password("testing1")
        )
    
    def test_login_with_wrong_password(self):
        authenticator = Authenticator(email_address="jd2@gmail.com", password="wrongpassword")
        response, status_code = authenticator.sign_in()
        
        self.assertEqual(status_code, 401)
        self.assertEqual(response["error"], "Invalid credentials")
    
    def test_login_with_wrong_email(self):
        authenticator = Authenticator(email_address="wrongemail@gmail.com", password="testing1")
        response, status_code = authenticator.sign_in()
        
        self.assertEqual(status_code, 401)
        self.assertEqual(response["error"], "Invalid credentials")
        

# All tests passed        
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
        

# All tests passed                
class SignUpValidationTest(TestCase):
    def test_sign_up_missing_fields(self):
        # Missing username and password
        incomplete_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@gmail.com"
        }  
        
        authenticator = Authenticator()
        response, status_code = authenticator.sign_up(incomplete_data)
        self.assertEqual(status_code, 400)
        self.assertEqual(response["error"], "Missing required fields")

    def test_sign_up_weak_password(self):
        weak_password_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "jane_doe",
            "email": "jane.doe@gmail.com",
            "password": "123"
        }
        
        authenticator = Authenticator()
        response, status_code = authenticator.sign_up(weak_password_data)
        self.assertEqual(status_code, 400)
        self.assertEqual(response["error"], "Password must be at least 8 characters long.")
    
    def test_sign_up_duplicate_username(self):
        RegisteredUser.objects.create(
            first_name="Jane",
            last_name="Doe",
            username="jane_doe",
            email="jane.doe@gmail.com",
            hashed_password=make_password("testing123")
        )
        
        duplicate_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "jane_doe",
            "email": "janedoe.new@gmail.com",
            "password": "testing123"
        }
        
        authenticator = Authenticator()
        response, status_code = authenticator.sign_up(duplicate_data)
        self.assertEqual(status_code, 400)
        self.assertEqual(response["error"], "Username already exists. Please choose another one.")
    
    def test_sign_up_duplicate_email(self):
        RegisteredUser.objects.create(
            first_name="Jane",
            last_name="Doe",
            username="janedoe1",
            email="jane.doe@gmail.com",
            hashed_password=make_password("testing123")
        )
        
        duplicate_email_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "janedoe2",
            "email": "jane.doe@gmail.com",
            "password": "testing123"
        }
        
        authenticator = Authenticator()
        response, status_code = authenticator.sign_up(duplicate_email_data)
        self.assertEqual(status_code, 400)
        self.assertEqual(response["error"], "User with this email already exists.")


# All tests passed                
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
        

# All tests passed                
class SaveManagerTest(TestCase):
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

        # Create a recipe
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            estimated_time="30",
            skill_level="Beginner",
            instructions="Test instructions"
        )

        # Instantiate the SaveManager
        self.save_manager = SaveManager(self.user)
        
    def test_from_token_valid_token(self):
        save_manager = SaveManager.from_token(self.token.token)
        self.assertIsInstance(save_manager, SaveManager)
        self.assertEqual(save_manager.user, self.user)

    def test_from_token_invalid_token(self):
        with self.assertRaises(ValueError) as context:
            SaveManager.from_token("invalid_token")
        self.assertEqual(str(context.exception), "Invalid token provided")

    def test_add_to_history_success(self):
        response = self.save_manager.add_to_history(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], "Recipe added to history successfully")
        self.assertTrue(self.user.last_used_recipes.filter(id=self.recipe.id).exists())

    def test_save_recipe_success(self):
        response = self.save_manager.save_recipe(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], "Recipe saved successfully")
        self.assertTrue(self.user.saved_recipes.filter(id=self.recipe.id).exists())

    def test_remove_saved_recipe_success(self):
        self.user.saved_recipes.add(self.recipe)
        response = self.save_manager.remove_saved_recipe(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], "Recipe successfully removed")
        self.assertFalse(self.user.saved_recipes.filter(id=self.recipe.id).exists())

    def test_remove_saved_recipe_not_found(self):
        response = self.save_manager.remove_saved_recipe(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], "Recipe does not exist for user")

    def test_clear_recipe_history_success(self):
        self.user.last_used_recipes.add(self.recipe)
        response = self.save_manager.clear_recipe_history()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], "Successfully cleared history")
        self.assertFalse(self.user.last_used_recipes.exists())

    def test_clear_recipe_history_already_empty(self):
        response = self.save_manager.clear_recipe_history()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], "History already empty")

    def test_view_saved_recipes_success(self):
        self.user.saved_recipes.add(self.recipe)
        response = self.save_manager.view_saved_recipes("saved")
        self.assertIsInstance(response, list)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["recipe_name"], self.recipe.title)

    def test_view_saved_recipes_empty(self):
        response = self.save_manager.view_saved_recipes("saved")
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "Saved recipes are empty")
        
    def test_view_saved_recipes_history_empty(self):
        response = self.save_manager.view_saved_recipes("history")
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "History is empty")

    def test_view_recipes_success(self):
        self.user.last_used_recipes.add(self.recipe)
        self.user.saved_recipes.add(self.recipe)
        response = self.save_manager.view_recipes()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["last_viewed"], [self.recipe.title])
        self.assertEqual(response_data["saved_recipes"], [self.recipe.title])


    def test_view_recipes_empty(self):
        response = self.save_manager.view_recipes()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {
            "last_viewed": [],
            "saved_recipes": []
        })
        

# All tests passed                
class RecipeParserTest(TestCase):
    def setUp(self):
        # Sample recipe data for testing
        self.valid_recipe_data = {
            "recipe": {
                "recipe_name": "Test Recipe",
                "time": "30",
                "skill_level": "Beginner",
                "ingredients": [{"name": "Ingredient 1"}, {"name": "Ingredient 2"}],
                "steps": ["Step 1", "Step 2"]
            }
        }

        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
        json.dump(self.valid_recipe_data, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        # Clean up the temporary file
        os.unlink(self.temp_file.name)

    def test_from_file_valid(self):
        parser = RecipeParser.from_file(self.temp_file.name)
        self.assertIsInstance(parser, RecipeParser)
        self.assertEqual(parser.recipe_data, self.valid_recipe_data["recipe"])

    def test_from_file_missing_fields(self):
        invalid_recipe_data = {
            "recipe": {
                "recipe_name": "Test Recipe",
                "time": "30",
                # Missing "skill_level", "ingredients", and "steps"
            }
        }

        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            json.dump(invalid_recipe_data, f)

        response = RecipeParser.from_file(self.temp_file.name)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "Missing required fields")

    def test_from_file_file_not_found(self):
        response = RecipeParser.from_file("nonexistent_file.json")
        self.assertEqual(response, ({"FileNotFound": "nonexistent_file.json does not exist or is in the wrong directory"}, 400))

    def test_from_file_permission_error(self):
        # Create a file with no read permissions
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as temp_file:
            temp_file_path = temp_file.name
            os.chmod(temp_file_path, 0o000)  # Remove all permissions

            response = RecipeParser.from_file(temp_file_path)
            self.assertEqual(response, ({"PermissionError": f"You do not have the correct permissions to access {temp_file_path}"}, 400))

            # Restore permissions to allow cleanup
            os.chmod(temp_file_path, 0o644)

    def test_to_model_valid(self):
        parser = RecipeParser(self.valid_recipe_data["recipe"])
        recipe = parser.to_model()

        self.assertIsInstance(recipe, Recipe)
        self.assertEqual(recipe.title, self.valid_recipe_data["recipe"]["recipe_name"])
        self.assertEqual(recipe.estimated_time, self.valid_recipe_data["recipe"]["time"])
        self.assertEqual(recipe.skill_level, self.valid_recipe_data["recipe"]["skill_level"])
        self.assertEqual(json.loads(recipe.instructions), self.valid_recipe_data["recipe"]["steps"])

        # Check ingredients
        ingredients = Ingredients.objects.filter(recipe=recipe)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(ingredients[0].ingredient, "Ingredient 1")
        self.assertEqual(ingredients[1].ingredient, "Ingredient 2")

    def test_to_model_no_recipe_data(self):
        parser = RecipeParser()
        with self.assertRaises(ValueError) as context:
            parser.to_model()
        self.assertEqual(str(context.exception), "No recipe data found in parser object.")
