# from django.shortcuts import render

# Create your views here.

import json
import os
import google.generativeai as genai

genai.configure(api_key="GEMINI_API_KEY")

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
    "dietary_restrictions": "Vegetarian",
    "ingredients": ["tomato", "cheese", "basil", "pasta"],
}

# Construct prompt
prompt = (
    f"Create a recipe using the following details:\n"
    f"- Skill Level: {test_input['skill_level']}\n"
    f"- Time: {test_input['time']} minutes\n"
    f"- Dietary Restrictions: {test_input['dietary_restrictions']}\n"
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
print(recipe_json)