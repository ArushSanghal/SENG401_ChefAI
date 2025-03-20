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
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import google.generativeai as genai
import json

from .models import Recipe, Ingredients

from .authentication import Authenticator
from .profile_manager import profileManager

import os

REGISTERED_USER_EXPIRY = 30

"""
Refactoring notes:
    Dependency injection for the api key,
    api key should live in a .env file
"""
class LLM:
    def __init__(self,):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY was not found in .env file")
        genai.configure(api_key=api_key)
        self.generation_config = {
            "temperature": 0,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }

        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config,
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
                return JsonResponse({"error": "Invalid JSON format received from API"}, status=400)
        return JsonResponse({"error": "No recipe generated"})

    def save_recipe(self, recipe_data):
        filename = "saved_recipe.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(recipe_data, file, indent=4)
        return filename

# class User:
#     def __init__(self, skill_level=None, available_time=None):
#         self.skill_level = skill_level
#         self.available_time = available_time

# class Guest():
#     def __init__(self, skill_level=None, available_time=None):
#         pass
#         # super().__init__(skill_level, available_time)

#     def sign_up(self, data):
#         required_fields = ["first_name", "last_name", "username", "email", "password"]
#         if not all(key in data for key in required_fields):
#             return {"error": "Missing required fields"}, 400

#         if len(data["password"]) < 8:
#             return {"error": "Password must be at least 8 characters long."}, 400

#         if RegisteredUser.objects.filter(username=data["username"]).exists():
#             return {"error": "Username already exists. Please choose another one."}, 400

#         if RegisteredUser.objects.filter(email=data["email"]).exists():
#             return {"error": "User with this email already exists."}, 400

#         hashed_pw = make_password(data["password"])  #Creates a hashed password
#         new_user = RegisteredUser.objects.create(
#             first_name=data["first_name"],
#             last_name=data["last_name"],
#             username=data["username"],
#             email=data["email"].strip().lower(),
#             hashed_password=hashed_pw,
#         )

#         return {"message": f"User {new_user.username} successfully registered"}, 201

# class Admin():
#     def __init__(self, email_address, password):
#         # super().__init__(None, None)
#         self.email_address = email_address
#         self.password = password

#     def manage_llm(self):
#         pass

#     def manage_account(self):
#         pass

#     def manage_database(self):
#         pass
    

"""
"""
class Recipe_Generator:
    def __init__(self, recipe_data=None, recipe=None):
        self.recipe_data = recipe_data
        self.recipe = recipe
        
    @classmethod
    def from_file(cls, filename="saved_recipe.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return {"FileNotFound": f"{filename} does not exist or is in the wrong directory"}, 400
        except PermissionError:
            return {"PermissionError": f"You do not have the correct permissions to access {self.filename}"}, 400
        except Exception as e:
            return {"Uknown error": e}, 400
        
        recipe_data = data.get("recipe", {})
        required_fields = ["recipe_name", "time", "skill_level", "ingredients","steps"]
        if not all(key in recipe_data for key in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)
        
        return cls(recipe_data=recipe_data)

    def save_recipe(self):
        # Save to database
        if self.recipe_data is None:
            return None
        
        new_recipe = Recipe.objects.create(
            title= self.recipe_data["recipe_name"],
            estimated_time = self.recipe_data["time"],
            skill_level = self.recipe_data["skill_level"],
            instructions=json.dumps(self.recipe_data["steps"])
        )

        for ingredient in self.recipe_data["ingredients"]:
            Ingredients.objects.create(
                ingredient = ingredient["name"],
                recipe = new_recipe
            )
        
        self.recipe = new_recipe
        return new_recipe

@csrf_exempt
@require_http_methods(["GET","POST"])
def generate_recipe(request):
    if request.method == "POST":
        # try:
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, TypeError) as je:
            return JsonResponse({"error": f"failed to load JSON {je}"}, status=400)
        
        required_fields = ["ingredients", "skill_level", "time"]

        if not all(key in data for key in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)
        
        llm = LLM()
        response = llm.generate_recipe(data["skill_level"], data["time"], data["dietary_restrictions"], data["ingredients"])

        llm.save_recipe(response)
        
        return JsonResponse(response)
        # except Exception as e:
        #     print(f"Unexpected Error: {str(e)}")
        #     return JsonResponse({"error": str(e)}, status=500)

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
        auth = Authenticator()
        response_data, status_code = auth.sign_up(data)
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

        authenticate_user = Authenticator(email, password)
        response_data, status_code = authenticate_user.sign_in()
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
        prof_man = profileManager()
        response_data, status_code = prof_man.get_user_data(token)
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
            prof_man = profileManager()
            response_data, status_code = prof_man.update_profile(token, data)
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
            authenticate_user = Authenticator()
            response_data, status_code = authenticate_user.logout(token)
            return JsonResponse(response_data, status=status_code)
        else:
            return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
