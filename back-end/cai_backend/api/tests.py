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
        

