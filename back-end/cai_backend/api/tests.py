from django.test import TestCase
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from .models import RegisteredUser, Recipe, Ingredients, Token, SkillLevelChoices
# from .views import Registered
from .services.profile_manager import ProfileManager
from .services.authenticator import Authenticator
from .services.save_manager import SaveManager
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
from django.http.response import JsonResponse



# class SaveRecipeTestCase(TestCase):
#     def setUp(self):
#         # Create a mock registered user
#         self.user = RegisteredUser.objects.create(
#             first_name="John",
#             last_name="Doe",
#             username="jd",
#             email="jd@gmail.com",
#             hashed_password=make_password("test")
#         )

#         # Instantiate the Registered user class from your code
#         self.registered = Registered(name="John Doe",username="jd",phone_number="1234567890", email_address="jd@gmail.com", password="test",available_time="Anytime")

#     def test_save_recipe(self):

#         self.registered.save_recipe()

#         # Assert the recipe was saved
#         recipe = Recipe.objects.get(title ="Quick Tomato Onion Sauce")
#         self.assertIsNotNone(recipe)
#         self.assertEqual(recipe.skill_level, "Advanced")

#         # Assert ingredients were saved
#         ingredients = Ingredients.objects.filter(recipe=recipe)
#         self.assertEqual(len(ingredients), 2)
#         self.assertEqual(ingredients[0].ingredient, "tomato")
#         self.assertEqual(ingredients[1].ingredient, "onion")





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
        self.profile_manager = ProfileManager(self.user)

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
        
        dietary_restrictions = list(self.user.dietary_restrictions.value_list("restriction",  flat=True)) # type: ignore
        self.assertEqual(len(dietary_restrictions), 1)
        self.assertEqual("Beef", dietary_restrictions)
        
    def test_update_profile_skill_level_only(self):
        new_data = {
            "skill_level": SkillLevelChoices.ADVANCED
        }
            
        response, status_code = self.profile_manager.update_profile(self.token.token, new_data)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"success": "Profile updated successfully"})
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.skill_level, SkillLevelChoices.ADVANCED)

    def test_update_profile_dietary_restrictions_only(self):
        new_data = {
            "dietary_restrictions": {"Beef", "Milk"}
        }
            
        response, status_code = self.profile_manager.update_profile(self.token.token, new_data)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"success": "Profile updated successfully"})
        
        self.user.refresh_from_db()
        dietary_restrictions = list(self.user.dietary_restrictions.values_list("restriction", flat=True)) # type: ignore
        self.assertEqual(len(dietary_restrictions), 2)
        self.assertIn("Beef", dietary_restrictions)
        self.assertIn("Milk", dietary_restrictions)
    
    def test_update_profile_empty_dietary_restrictions(self):
        new_data = {
            "dietary_restrictions": []
        }
            
        response, status_code = self.profile_manager.update_profile(self.token.token, new_data)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response, {"success": "Profile updated successfully"})
        
        self.user.refresh_from_db()
        dietary_restrictions = list(self.user.dietary_restrictions.values_list("restriction", flat=True)) # type: ignore
        self.assertEqual(len(dietary_restrictions), 0)
    
    def test_update_profile_invalid_token(self):
        response, status_code = self.profile_manager.update_profile("invalid_token", {"skill_level": SkillLevelChoices.INTERMEDIATE})
        self.assertEqual(status_code, 401)
        self.assertEqual(response["error"], "Invalid token")
        
    def test_update_profile_expired_token(self):
        expired_token = Token.objects.create(
            user=self.user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() - timedelta(minutes=10)
        )
        response, status_code = self.profile_manager.update_profile(expired_token.token, {"skill_level": SkillLevelChoices.INTERMEDIATE})
        self.assertEqual(status_code, 401)
        self.assertEqual(response["error"], "Invalid token")

    def test_update_profile_non_existent_user(self):
        non_existent_user_token = Token.objects.create(
            user=None,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        new_data = {
            "skill_level": SkillLevelChoices.INTERMEDIATE
        }
            
        response, status_code = self.profile_manager.update_profile(non_existent_user_token.token, new_data)
        
        self.assertEqual(status_code, 404)
        self.assertEqual(response, {"error": "User not found"})

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

        # Create a token with no associated user
        self.token_with_no_user = Token.objects.create(
            user=None,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(minutes=10)
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

    def test_get_user_data_non_existent_user(self):
        response, status_code = self.profile_manager.get_user_data(self.token_with_no_user.token)
        
        self.assertEqual(status_code, 404)
        self.assertEqual(response["error"], "User not found")


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
        self.assertEqual(response.json(), {"message": "Recipe added to history successfully"})
        self.assertTrue(self.user.last_used_recipes.filter(id=self.recipe.id).exists())

    def test_add_to_history_user_not_found(self):
        self.user.delete()
        response = self.save_manager.add_to_history(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "User not found"})
        
        # Recreate the user to ensure isolation for other tests
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd2",
            email="jd2@gmail.com",
            hashed_password="hashed_password"
        )
        self.save_manager = SaveManager(self.user)

    def test_save_recipe_success(self):
        response = self.save_manager.save_recipe(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Recipe saved successfully"})
        self.assertTrue(self.user.saved_recipes.filter(id=self.recipe.id).exists())

    def test_save_recipe_user_not_found(self):
        self.user.delete()
        response = self.save_manager.save_recipe(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "User not found"})
        
        # Recreate the user to ensure isolation for other tests
        self.user = RegisteredUser.objects.create(
            first_name="John",
            last_name="Doe",
            username="jd2",
            email="jd2@gmail.com",
            hashed_password="hashed_password"
        )
        self.save_manager = SaveManager(self.user)

    def test_remove_saved_recipe_success(self):
        self.user.saved_recipes.add(self.recipe)
        response = self.save_manager.remove_saved_recipe(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Recipe successfully removed"})
        self.assertFalse(self.user.saved_recipes.filter(id=self.recipe.id).exists())

    def test_remove_saved_recipe_not_found(self):
        response = self.save_manager.remove_saved_recipe(self.recipe)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Recipe does not exist for user"})

    def test_clear_recipe_history_success(self):
        self.user.last_used_recipes.add(self.recipe)
        response = self.save_manager.clear_recipe_history()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Successfully cleared history"})
        self.assertFalse(self.user.last_used_recipes.exists())

    def test_clear_recipe_history_already_empty(self):
        response = self.save_manager.clear_recipe_history()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "History already empty"})

    def test_view_saved_recipes_success(self):
        self.user.saved_recipes.add(self.recipe)
        response = self.save_manager.view_saved_recipes()
        self.assertIsInstance(response, list)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["recipe_name"], self.recipe.title)

    def test_view_saved_recipes_empty(self):
        response = self.save_manager.view_saved_recipes()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"error": "Saved history is empty"})

    def test_view_recipes_success(self):
        self.user.last_used_recipes.add(self.recipe)
        self.user.saved_recipes.add(self.recipe)
        response = self.save_manager.view_recipes()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "last_viewed": [self.recipe.title],
            "saved_recipes": [self.recipe.title]
        })

    def test_view_recipes_empty(self):
        response = self.save_manager.view_recipes()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "last_viewed": [],
            "saved_recipes": []
        })