from django.http import JsonResponse
from .models import RegisteredUser, Recipe

class RecipeManager:
    def __init__(self, user=None):
        self.user = user
    
    
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
