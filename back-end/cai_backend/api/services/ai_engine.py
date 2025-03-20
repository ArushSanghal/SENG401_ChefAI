from django.http import JsonResponse
from google import generativeai as genai
from google.generativeai.types import GenerationConfig
import json
import os

class AIEngine:
    """Class takes care of instantiating the LLM as a singleton. If it's used more than once,
       the model returns the singleton object"""
    _instance = None

    def __new__(cls, api_key=None):
        if cls._instance is None:
            cls._instance = super(AIEngine, cls).__new__(cls)
            cls._instance._initialize(api_key)
        return cls._instance

    def _initialize(self, api_key=None):
        """Initializes the Gemini model and configuration."""
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY was not found in environment variables")

        genai.configure(api_key=api_key)

        self.generation_config = GenerationConfig(
            temperature=0,
            top_p=1,
            top_k=1,
            max_output_tokens=8192,
            response_mime_type="application/json"
        )

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

    def generate_recipe_json(self, skill_level, available_time, 
                             dietary_restrictions, ingredients):

        prompt = (
            f"Create a recipe using the following details:\n"
            f"- Skill Level: {skill_level}\n"
            f"- Time: {available_time} minutes\n"
            f"- Dietary Restrictions: {", ".join(dietary_restrictions) \
                                       if dietary_restrictions else "None"}\n"
            f"- Ingredients: {', '.join(ingredients)}\n"
             "Provide a JSON output following the exact format given in the \
                system instruction."
        )

        try:
            response = self.model.generate_content(prompt)

            if not response:
                return JsonResponse({"error": "Empty response from API."}, status=400)

            return json.loads(response.text.strip())
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({"error": "Invalid JSON response from API."}, status=400)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return JsonResponse({"error": f"An unexpected error occurred: {e}"}, status=400)