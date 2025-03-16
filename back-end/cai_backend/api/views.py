from django.http import JsonResponse
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

'''
FOR REFERENCE PURPOSES ONLY
# Create the model
generation_config = {
  "temperature": 0,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json" # for better use in implementation for frontend use 
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
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

# Example test input 
test_input = {
    "skill_level": "Beginner",
    "time": "30",
    "dietary_restrictions": [],
    "ingredients": ["tomato", "cheese", "basil", "rice", "tofu"],
}

# Format dietary restrictions as a comma-separated string, or "None" if empty
dietary_str = ", ".join(test_input["dietary_restrictions"]) if test_input["dietary_restrictions"] else "None"

# Construct prompt
prompt = (
    f"Create a recipe using the following details:\n"
    f"- Skill Level: {test_input['skill_level']}\n"
    f"- Time: {test_input['time']} minutes\n"
    f"- Dietary Restrictions: {dietary_str}\n"
    f"- Ingredients: {', '.join(test_input['ingredients'])}\n"
    f"Provide a JSON output following the exact format given in the system instruction."
)

# Generate new recipe
print("\nGenerating new recipe...\n")
response = model.generate_content(prompt)

# Extract recipe text
recipe_json = response.text if response.text else "{}"

# Define JSON file path
json_filename = "saved_recipe.json"

# Overwrite JSON file with new recipe
with open(json_filename, "w", encoding="utf-8") as file:
    json.dump({"recipe": recipe_json}, file, indent=4)

# Print the new recipe
print("\nGenerated Recipe:\n")
# print(recipe_json)

'''

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import RegisteredUser, Recipe
from django.contrib.auth.hashers import make_password, check_password
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


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

            return JsonResponse(response)
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)