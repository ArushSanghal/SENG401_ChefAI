from .models import RegisteredUser, Recipe

class RecipeManager:
    def __init__(self, user:RegisteredUser):
        self.user = user
    
    def add_to_history(self, recipe:Recipe):
        try:
            self.user.add_viewed_recipe(recipe)
            return {"message": "Recipe added to history successfully"}
        except RegisteredUser.DoesNotExist:
            return {"error": "User not found"}

    def save_recipe(self, recipe:Recipe):
        try:
            self.user.saved_recipes.add(recipe)
            return {"message": "Recipe saved successfully"}
        except RegisteredUser.DoesNotExist:
            return {"error": "User not found"}

    def remove_saved_recipe(self, recipe:Recipe):
        if self.user.saved_recipes.filter(id=recipe.id).exists():
            self.user.saved_recipes.remove(recipe)
            return {"message": "Recipe successfully removed"}
        else:
            return {"error": "Recipe does not exist for user"}
        
    def clear_recipe_history(self):
        if self.user.last_used_recipes.exists():
            self.user.last_used_recipes.all().delete()
            return {"message": "Successfully cleared history"}
        else:
            return {"error": "History already empty"}

    def view_recipes(self, num_rows:int=5):
        last_recipes = self.user.last_used_recipes.all().order_by('-id')[:num_rows]
        saved_recipes = self.user.saved_recipes.all()
        return {
            "last_viewed": [recipe.title for recipe in last_recipes],
            "saved_recipes": [recipe.title for recipe in saved_recipes]
        }

    # def add_to_history(self):
    #     recipe = Recipe_Generator()
    #     new_recipe = recipe.parse_recipe()

    #     try:
    #         reg_user = RegisteredUser.objects.get(username=self.username)
    #         reg_user.add_viewed_recipe(new_recipe)
    #     except:
    #         return JsonResponse({"error": "User not found"}, status=404)

    #     return JsonResponse({"message": "Recipe saved successfully"}, status=201)


    # def save_recipe(self):
    #     recipe = Recipe_Generator()
    #     new_recipe = recipe.parse_recipe()

    #     try:
    #         reg_user = RegisteredUser.objects.get(username=self.username)
    #         reg_user.saved_recipes.add(new_recipe)
    #     except RegisteredUser.DoesNotExist:
    #         return JsonResponse({"error": "User not found"}, status=404)

    #     return JsonResponse({"message": "Recipe saved successfully"}, status=201)