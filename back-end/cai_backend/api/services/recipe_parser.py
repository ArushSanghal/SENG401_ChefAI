from django.http.response import JsonResponse
from ..models import Recipe, Ingredients
import json

class RecipeParser:
    def __init__(self, recipe_data=None):
        self.recipe_data = recipe_data
        
    @classmethod
    def from_file(cls, filename="saved_recipe.json"):
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
        
        return cls(recipe_data=recipe_data)

    def to_model(self):
        # Save to database
        if self.recipe_data is None:
            raise ValueError("No recipe data found in parser object.")
        
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
        
        return new_recipe
    
    def to_file(self, filename:str):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.recipe_data, file, indent=4)