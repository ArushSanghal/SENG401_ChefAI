from ..models import RegisteredUser, Recipe, Token
from django.http.response import JsonResponse

class SaveManager:
    def __init__(self, user: RegisteredUser):
        self.user = user

    @classmethod
    def from_token(cls, token: str):
        token_obj = Token.objects.filter(token=token).first()
        if token_obj is None:
            raise ValueError("Invalid token provided")
        return cls(user=token_obj.user)
    
    def add_to_history(self, recipe: Recipe):
        try:
            self.user.add_viewed_recipe(recipe)
            return JsonResponse({"message": "Recipe added to history successfully"}, status=200)
        except RegisteredUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    def save_recipe(self, recipe: Recipe):
        try:
            self.user.saved_recipes.add(recipe)
            return JsonResponse({"message": "Recipe saved successfully"}, status=200)
        except RegisteredUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    def remove_saved_recipe(self, recipe: Recipe):
        if self.user.saved_recipes.filter(id=recipe.pk).exists():
            self.user.saved_recipes.remove(recipe)
            return JsonResponse({"message": "Recipe successfully removed"}, status=200)
        else:
            return JsonResponse({"error": "Recipe does not exist for user"}, status=404)
        
    def clear_recipe_history(self):
        if self.user.last_used_recipes.exists():
            self.user.last_used_recipes.all().delete()
            return JsonResponse({"message": "Successfully cleared history"}, status=200)
        else:
            return JsonResponse({"error": "History already empty"}, status=400)

    def view_saved_recipes(self, recipe_type="saved"):
        if recipe_type == "saved":
            recipes = self.user.saved_recipes.all()
        elif recipe_type == "history":
            recipes = self.user.last_used_recipes.all()
        else:
            return JsonResponse({"error": "Invalid recipe type provided"}, status=400)

        if recipes.exists():
            json_recipes = []
            for recipe in recipes:
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
            return json_recipes
        else:
            return JsonResponse({"error": f"No {recipe_type} recipes found"}, status=404)

    def save_last_viewed_recipe(self):
        if self.user.last_used_recipes.exists():
            self.user.saved_recipes.add(self.user.last_used_recipes.order_by('-id').first())
            return JsonResponse({"message": "Successfully added recipe to favourites."}, status=200)
        else:
            return JsonResponse({"error": "Failed to find any recipes in history."}, status=400)

    def view_recipes(self, num_rows: int = 5):
        last_recipes = self.user.last_used_recipes.all().order_by('-id')[:num_rows]
        saved_recipes = self.user.saved_recipes.all()
        return JsonResponse({
            "last_viewed": [recipe.title for recipe in last_recipes],
            "saved_recipes": [recipe.title for recipe in saved_recipes]
        }, status=200)