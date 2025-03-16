from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import RegisteredUser, Recipe
from django.contrib.auth.hashers import make_password, check_password
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import RegisteredUser, Recipe
from django.contrib.auth.hashers import make_password, check_password
# from django.shortcuts import render

# Create your views here.

import json
import google.generativeai as genai

genai.configure(api_key="AIzaSyAnDxD9kAbcngSDw61KjeJzqiqfdCo_sSI")

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
                return {"error": "Invalid JSON format received from API"}
        return {"error": "No recipe generated"}

    def save_recipe(self, recipe_data):
        filename = "saved_recipe.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(recipe_data, file, indent=4)
        return filename



# Create your views here.
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
        

# Create your views here.

class User:
    def __init__(self, skill_level, available_time):
        self.skill_level = skill_level
        self.available_time = available_time

    def create_recipe(self):
        pass

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


class Registered(User):
    def __init__(self, name, phone_number, email_address, password, available_time):
        super().__init__(None, available_time)
        self.name = name
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

    def save_recipe(self, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = RegisteredUser.objects.get(email=self.email_address)
        user.saved_recipes.add(recipe)
        return f"Recipe '{recipe.title}' saved successfully"

    def view_recipes(self):
        user = RegisteredUser.objects.get(email=self.email_address)
        last_recipes = user.last_used_recipes.all().order_by('-id')[:5]
        saved_recipes = user.saved_recipes.all()
        return {
            "last_viewed": [recipe.title for recipe in last_recipes],
            "saved_recipes": [recipe.title for recipe in saved_recipes]
        }
    
class Recipe:
    def __init__(self, ingredient_list, recipe_id, title):
        self.ingredient_list = ingredient_list
        self.recipe_id = recipe_id
        self.title = title

    def generate_recipe(self):
        pass


# class LLM:
#     def __init__(self, skill_level, available_time, ingredients, prompt, title):
#         self.skill_level = skill_level
#         self.available_time = available_time
#         self.ingredients = ingredients
#         self.prompt = prompt
#         self.title = title

#     def generate_recipe(self):
#         pass

#     def save_recipe(self):
#         pass
