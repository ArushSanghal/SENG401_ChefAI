# from django.shortcuts import render

# Create your views here.

import os
import google.generativeai as genai

genai.configure(api_key="GEMINI_API_KEY")

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
#   "response_mime_type": "application/json" # for better use in implementation for frontend use 
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  system_instruction=(
  "Generate personalized recipes based on the user's cooking skill level, "
  "available time, dietary restrictions, and available ingredients. Provide a detailed recipe, "
  "including an ingredient list, step-by-step instructions, estimated preparation and cooking time, "
  "and serving size. Use a friendly and encouraging tone, ensure instructions are clear and concise, "
  " and offer helpful tips or substitutions to accommodate various skill levels."
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
    f"Provide a clear step-by-step recipe."
)

response = model.generate_content(prompt)

print("\nGenerated Recipe:\n")
print(response.text if response.text else "No recipe found.")