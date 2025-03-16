from django.db import models

class TimeChoices(models.TextChoices):
    MIN_15 = "15", "15 minutes"
    MIN_30 = "30", "30 minutes"
    MIN_45 = "45", "45 minutes"
    MIN_60 = "60", "1 hour"
    MIN_90 = "90", "1.5 hours"
    MIN_120 = "120", "2 hours"

class SkillLevelChoices(models.TextChoices):
    BEGINNER = "Beginner", "Beginner"
    INTERMEDIATE = "Intermediate", "Intermediate"
    ADVANCED = "Advanced", "Advanced"

class User(models.Model):
    """Stores general information about the user, dropped after use if they are not needed"""
    available_time = models.CharField(
        max_length=3,
        choices=TimeChoices.choices,
        default=TimeChoices.MIN_30
    )
    skill_level = models.CharField(
        max_length=12,
        choices=SkillLevelChoices.choices,
        default=SkillLevelChoices.BEGINNER
    )

class DietaryRestriction(models.Model):
    user = models.ForeignKey(User, related_name="dietary_restrictions", on_delete=models.CASCADE)
    restriction = models.CharField(max_length=200, blank=True, help_text="Dietary restrictions, seperated by a comma (,)")

class Recipe(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    estimated_time = models.CharField(
        max_length=3,
        choices=TimeChoices.choices,
        default=TimeChoices.MIN_30
    )
    skill_level = models.CharField(
        max_length=12,
        choices=SkillLevelChoices.choices,
        default=SkillLevelChoices.BEGINNER
    )
    instructions = models.CharField(max_length=250, blank=False, null=False)

class Ingredients(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
    ingredient = models.CharField(max_length=50, blank=False, null=False)

class RegisteredUser(User):
    """Information about logged in user, boolean provides admin privelages"""
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)
    email = models.EmailField(max_length=254, blank=False, null=False)
    hashed_password = models.CharField(max_length=254, blank=False, null=False)
    is_admin = models.BooleanField(default=False)
    saved_recipes = models.ManyToManyField(Recipe, related_name="saved_recipes", blank=True)
    last_used_recipes = models.ManyToManyField(Recipe, related_name="last_used_recipes", blank=True)

    def add_viewed_recipe(self, recipe):
        """Adds new recipes up to 5, uses FIFO to drop the oldest viewed recipe"""
        self.last_used_recipes.add(recipe)

        if self.last_used_recipes.count() > 5:
            first_viewed = self.last_used_recipes.all().order_by("id").first()
            self.last_used_recipes.remove(first_viewed)