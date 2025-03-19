from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import google.generativeai as genai
import json

from .models import RegisteredUser, Recipe, Ingredients


genai.configure(api_key="AIzaSyAnDxD9kAbcngSDw61KjeJzqiqfdCo_sSI") # type: ignore

class LLM:
    def __init__(self):
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


# Create your views here.

class User:
    def __init__(self, skill_level, available_time):
        self.skill_level = skill_level
        self.available_time = available_time

            
    def restrictions(self):
        pass

class Guest(User):
    def __init__(self, skill_level, available_time):
        super().__init__(skill_level, available_time)

    def sign_up(self, f_name, l_name, user_name, email_address, password):
            if RegisteredUser.objects.filter(email=email_address).exists():
                return "User already exists"
            
            hashed_pw = make_password(password)  
            new_user = RegisteredUser.objects.create(
                first_name=f_name,
                last_name=l_name,
                username=user_name,  
                email=email_address,
                hashed_password=hashed_pw,
            )
            return f"User {new_user.username} successfully registered"


# class Admin(User):
#     def __init__(self, email_address, password):
#         super().__init__(None, None)
#         self.email_address = email_address
#         self.password = password

#     def manage_llm(self):
#         pass

#     def manage_account(self):
#         pass

#     def manage_database(self):
#         pass


class Registered(User):
    def __init__(self, name, username, phone_number, email_address, password, available_time):
        super().__init__(None, available_time)
        self.name = name
        self.username = username
        self.phone_number = phone_number
        self.email_address = email_address
        self.password = password
        self.favourite_recipe = None
        self.last_few_recipes = []

    def sign_in(email_address, password):
        user = RegisteredUser.objects.filter(email=email_address).first()
        if user and check_password(password, user.hashed_password):
            return f"Welcome back, {user.first_name}!"
        return "Invalid credentials"

    def add_to_history(self):
        recipe = Recipe_Generator()
        new_recipe = recipe.parse_recipe()

        try:
            reg_user = RegisteredUser.objects.get(username=self.username)
            reg_user.add_to_history(new_recipe)
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
    
class Recipe_Generator:
    def __init__(self):
        pass

    def parse_recipe(self):
        f = open('saved_recipe.json')   # Parse the latest saved recipe

        data = json.load(f)
        recipe_data = data.get("recipe", {})

        required_fields = ["recipe_name", "time", "skill_level", "ingredients","steps"]

        if not all(key in recipe_data for key in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)
        
        # Save to database and create new object
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
