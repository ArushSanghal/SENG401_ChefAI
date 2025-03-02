from django.db import models

class User(models.Model):
    """Stores general information about the user, dropped after use if they are not necessary"""
    available_time = models.TextChoices("Avaiable_Time_Minutes", "15 30 45 60 90 120")
    skill_level = models.TextChoices("Skill_Level", "Beginner Intermediate Advanced")

class DietaryRestriction(models.Model):
    user = models.ForeignKey(User, related_name="dietary_restrictions", on_delete=models.CASCADE)
    restriction = models.CharField(max_length=200, blank=True, help_text="Dietary restrictions, seperated by a comma (,)")

class RegisteredUser(User):
    """Information about logged in user, boolean provides admin privelages"""
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    username = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(max_length=254, blank=False, null=False)
    hashed_password = models.charField(max_length=254, blank=False, null=False)
    is_admin = models.BooleanField(default=False)
    saved_recipes = models.ManyToManyField(Recipe, related_name="saved_recipes", blank=True)
    last_used_recipes = models.ManyToManyField(Recipe, related_name="last_used_recipes", blank=True)

    def add_viewed_recipe(self, recipe):
        """Adds new recipes up to 5, uses FIFO to drop the oldest viewed recipe"""
        from django.db.models. import Count
        self.last_used_recipes.add(recipe)

        if self.last_used_recipes.count() > 5:
            self.last_viewed_recipes.remove(self.last_viewed_recipes.all().order_by("id").first())

class Recipe(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    estimated_time = models.TextChoices("estimated_time", "15 30 45 60 90 120")
    skill_level = models.TextChoices("Skill_Level", "Beginner Intermediate Advanced")
    instructions = models.CharField(max_length=250, blank=False, null=False)

class Ingredients(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
    ingredient = models.CharField(max_length=50, blank=False, null=False)
