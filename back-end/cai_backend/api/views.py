"""
    Overall refactoring notes:
    Adjust each class based on its notes
    Test debug at every step along the way
    Refactor the classes to live OUTSIDE this file

    This file should only contain the "controllers" for our functions
    No data should be passed directly from action to DB

    Last note,
    change all model access to be SQL based (if time, for the sake of project)

    Go over functionality, make sure everything is present
"""


from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.utils import timezone
from datetime import timedelta
import google.generativeai as genai
import json

from .models import RegisteredUser, DietaryRestriction, SkillLevelChoices, Token, Recipe, Ingredients

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

REGISTERED_USER_EXPIRY = 30

"""
Refactoring notes:
    Dependency injection for the api key,
    api key should live in a .env file
"""
class LLM:
    def __init__(self):
        genai.configure(api_key="AIzaSyAWLFIGVTdsn-OxejhBhkzK4tbyKhc8hoM")
        self.generation_config = {
            "temperature": 0,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }

        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config, # type: ignore
            system_instruction=(
                "Generate a structured JSON recipe with the following format:\n"
                "{\n"
                '  "recipe": {\n'
                '    "recipe_name": "string",\n'
                '    "skill_level": "Beginner/Intermediate/Advanced",\n'
                '    "time": "string (e.g., 30 minutes)",\n'
                '    "dietary_restrictions": "string",\n'
                '    "ingredients": [\n'
                '      {"name": "string", "amount": "string", "unit": "string or null"}\n'
                '    ],\n'
                '    "steps": [\n'
                '      {"step": int, "instruction": "string"}\n'
                '    ],\n'
                '    "prep_time": "string",\n'
                '    "cook_time": "string",\n'
                '    "servings": "string",\n'
                '    "tips": ["string"],\n'
                '    "substitutions": [\n'
                '      {"ingredient": "string", "substitute": "string"}\n'
                '    ]\n'
                '  }\n'
                "}\n"
                "Ensure all keys match exactly and do not change key names."
            ),
        )

    def generate_recipe(self, skill_level, available_time, dietary_restrictions, ingredients):
        dietary_restrictions = ", ".join(dietary_restrictions) if dietary_restrictions else "None"

        prompt = (
            f"Create a recipe using the following details:\n"
            f"- Skill Level: {skill_level}\n"
            f"- Time: {available_time} minutes\n"
            f"- Dietary Restrictions: {dietary_restrictions}\n"
            f"- Ingredients: {', '.join(ingredients)}\n"
            f"Provide a JSON output following the exact format given in the system instruction."
        )

        response = self.model.generate_content(prompt)

        if response.text:
            try:
                recipe_json = json.loads(response.text)
                return recipe_json
            except json.JSONDecodeError:
                return {"error": "Invalid JSON format received from API"}
        return {"error": "No recipe generated"}

    def save_recipe(self, recipe_data):
        filename = "saved_recipe.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(recipe_data, file, indent=4)
        return filename

class User:
    def __init__(self, skill_level=None, available_time=None):
        self.skill_level = skill_level
        self.available_time = available_time

class Guest(User):
    def __init__(self, skill_level=None, available_time=None):
        super().__init__(skill_level, available_time)

    def sign_up(self, data):
        required_fields = ["first_name", "last_name", "username", "email", "password"]
        if not all(key in data for key in required_fields):
            return {"error": "Missing required fields"}, 400

        if len(data["password"]) < 8:
            return {"error": "Password must be at least 8 characters long."}, 400

        if RegisteredUser.objects.filter(username=data["username"]).exists():
            return {"error": "Username already exists. Please choose another one."}, 400

        if RegisteredUser.objects.filter(email=data["email"]).exists():
            return {"error": "User with this email already exists."}, 400

        hashed_pw = make_password(data["password"])  #Creates a hashed password
        new_user = RegisteredUser.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"],
            email=data["email"].strip().lower(),
            hashed_password=hashed_pw,
        )

        return {"message": f"User {new_user.username} successfully registered"}, 201

class Admin(User):
    def __init__(self, email_address, password):
        super().__init__(None, None)
        self.email_address = email_address
        self.password = password

    def manage_llm(self):
        pass

    def manage_account(self):
        pass

    def manage_database(self):
        pass
    

"""
    It's technically not a recipe generator, but this class is good,
    maybe add a dependency injection for the filename instead of hardcoding it
"""
class Recipe_Generator:
    @staticmethod
    def parse_recipe(filename="saved_recipe.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return {"FileNotFound": f"{filename} does not exist or is in the wrong directory"}, 400
        except PermissionError:
            return {"PermissionError": f"You do not have the correct permissions to access {filename}"}, 400
        except Exception as e:
            return {"Uknown error": e}, 400
        
        recipe_data = data.get("recipe", {})
        required_fields = ["recipe_name", "time", "skill_level", "ingredients","steps"]
        if not all(key in recipe_data for key in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Refactor, use SQL instead of django object        
        new_recipe = Recipe.objects.create(
            title= recipe_data["recipe_name"],
            estimated_time = recipe_data["time"],
            skill_level = recipe_data["skill_level"],
            instructions=json.dumps(recipe_data["steps"]) #saves as a json string
        )

        for ingredient in recipe_data["ingredients"]:
            Ingredients.objects.create(
                ingredient = ingredient["name"],
                recipe = new_recipe
            )
        
        return new_recipe

"""
Refactoring notes:
    Currently handles
        Authentication
        Profile management
        Receipe related functions
    Follow the single responsibility principle and break this down into multiple classes
    Potentially removing this class and creating, "controllers" for the features listed
"""
class Registered(User):
    def __init__(self, email_address=None, password=None, user=None):
        super().__init__(None, None)
        self.email_address = email_address.strip().lower() if email_address else None
        self.password = password
        self.user = user

    def sign_in(self):
        user = RegisteredUser.objects.filter(email=self.email_address).first()
        if user and check_password(self.password, user.hashed_password):
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            expires_at = timezone.now() + timedelta(minutes=10)

            #Token In Database
            Token.objects.create(user=user, token=access_token, expires_at=expires_at)

            return {
                "message": f"Welcome back, {user.first_name}!",
                "is_admin": user.is_admin,
                "refresh": str(refresh),
                "access": access_token,
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "skill_level": user.skill_level,
                "dietary_restrictions": list(user.dietary_restrictions.values_list("restriction", flat=True)),
            }, 200
        return {"error": "Invalid credentials"}, 401

    def get_user_data(self, token):
        db_token = Token.objects.filter(token=token).first()   #Checks token
        if not db_token or not db_token.is_valid():
            return {"error": "Invalid or expired token"}, 401

        user = db_token.user
        if not user:
            return {"error": "User not found"}, 404

        return {
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "skill_level": user.skill_level,
            "dietary_restrictions": list(user.dietary_restrictions.values_list("restriction", flat=True)),
        }, 200

    def update_profile(self, token, data):
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user_id = validated_token["user_id"]

            user = RegisteredUser.objects.filter(id=user_id).first()
            if not user:
                return {"error": "User not found"}, 404

            #Skill level
            skill_level = data.get("skill_level")
            if skill_level and skill_level in [choice[0] for choice in SkillLevelChoices.choices]:
                user.skill_level = skill_level

            #Dietary restrictions
            dietary_restrictions = data.get("dietary_restrictions", [])
            user.dietary_restrictions.all().delete()
            for restriction in dietary_restrictions:
                DietaryRestriction.objects.create(user=user, restriction=restriction)

            user.save()
            return {"success": "Profile updated successfully"}, 200
        except (InvalidToken, TokenError) as e:
            print(f"Token error: {e}")
            return {"error": "Invalid token"}, 401

    def logout(self, token):
        Token.objects.filter(token=token).delete()  #Deletes token from database
        return {"message": "Logged out successfully"}, 200

    def add_to_history(self):
        recipe = Recipe_Generator()
        new_recipe = recipe.parse_recipe()

        try:
            reg_user = RegisteredUser.objects.get(username=self.username)
            reg_user.add_viewed_recipe(new_recipe)
        except:
            return JsonResponse({"error": "User not found"}, status=404)

        return JsonResponse({"message": "Recipe saved successfully"}, status=201)


    def save_recipe(self):
        recipe = Recipe_Generator()
        new_recipe = recipe.parse_recipe()

        try:
            reg_user = RegisteredUser.objects.get(username=self.username)
            reg_user.saved_recipes.add(new_recipe)
        except RegisteredUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        return JsonResponse({"message": "Recipe saved successfully"}, status=201)


    def view_recipes(self):
        user = RegisteredUser.objects.get(email=self.email_address)
        last_recipes = user.last_used_recipes.all().order_by('-id')[:5]
        saved_recipes = user.saved_recipes.all()
        return {
            "last_viewed": [recipe.title for recipe in last_recipes],
            "saved_recipes": [recipe.title for recipe in saved_recipes]
        }

@csrf_exempt
@require_http_methods(["GET","POST"])
def generate_recipe(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            required_fields = ["ingredients", "skill_level", "time"]
            if not all(key in data for key in required_fields):
                return JsonResponse({"error": "Missing required fields"}, status=400)
            
            llm = LLM()
            response = llm.generate_recipe(data["skill_level"], data["time"], data["dietary_restrictions"], data["ingredients"])

            llm.save_recipe(response)

            return JsonResponse(response)
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def register_user(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        body_unicode = request.body.decode("utf-8")
        data = json.loads(body_unicode)
        guest = Guest()
        response_data, status_code = guest.sign_up(data)
        return JsonResponse(response_data, status=status_code)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def login_user(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        body_unicode = request.body.decode("utf-8")
        data = json.loads(body_unicode)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Missing email or password"}, status=400)

        registered_user = Registered(email, password)
        response_data, status_code = registered_user.sign_in()
        return JsonResponse(response_data, status=status_code)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_user_data(request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        registered_user = Registered()
        response_data, status_code = registered_user.get_user_data(token)
        return JsonResponse(response_data, status=status_code)
    else:
        return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)

@csrf_exempt
@require_http_methods(["POST"])
def update_user_profile(request):
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            body_unicode = request.body.decode("utf-8")
            data = json.loads(body_unicode)
            registered_user = Registered()
            response_data, status_code = registered_user.update_profile(token, data)
            return JsonResponse(response_data, status=status_code)
        else:
            return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def logout_user(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            registered_user = Registered()
            response_data, status_code = registered_user.logout(token)
            return JsonResponse(response_data, status=status_code)
        else:
            return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def save_button(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = request.headers.get("Authorization").split(" ")[1]

            db_token = Token.objects.filter(token=token).first()
            if not db_token:
                return JsonResponse({"error": "Invalid or expired token"}, status=401)

            user = db_token.user
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            recipe = Recipe_Generator() 
            new_recipe = recipe.parse_recipe()

            user.saved_recipes.add(new_recipe)
            user.save() 

            return JsonResponse({"message": "Recipe saved successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def view_recipes(request):
     if request.method == "GET":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            db_token = Token.objects.filter(token=token).first()
            if not db_token:
                return JsonResponse({"error": "Invalid or expired token"}, status=401)

            user = db_token.user
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)
            
            saved_recipes = user.saved_recipes.all()
            
            if not saved_recipes.exists():
               return JsonResponse({"saved_recipes": "No saved recipes"}, status=200)

            json_recipes = []

            for recipe in saved_recipes:
                ingredient_list = []
                ingredients = recipe.ingredients.all()
                for ingredient in ingredients:
                    ingredient_list.append(ingredient.ingredient)


                recipe_data = {
                        "recipe_name": recipe.title,
                        "estimated_time": recipe.estimated_time, 
                        "skill_level": recipe.skill_level,
                        "ingredients": ', '.join(ingredient_list),
                        "instructions": recipe.instructions,
                    }
                json_recipes.append(recipe_data)
            

            return JsonResponse({"saved_recipes": json_recipes}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)