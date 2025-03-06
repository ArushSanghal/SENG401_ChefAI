from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import RegisteredUser, Recipe
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.

class User:
    def __init__(self, skill_level, available_time):
        self.skill_level = skill_level
        self.available_time = available_time

    def create_recipe(self):
        pass

    def restrictions(self):
        pass


class Guest(User):
    def __init__(self, skill_level, available_time):
        super().__init__(skill_level, available_time)

    def sign_up(self, f_name, l_name, user_name, email_address, password):
            if RegisteredUser.objects.filter(email=email_address).exists():
                return "User already exists"
            
            hashed_pw = make_password(password)  
            new_user = RegisteredUser.objects.create(
                first_name=f_name,
                last_name=l_name,
                username=user_name,  
                email=email_address,
                hashed_password=hashed_pw,
            )
            return f"User {new_user.username} successfully registered"


class Admin(User):
    def __init__(self, email_address, password):
        super().__init__(None, None)
        self.email_address = email_address
        self.password = password

    def manage_llm(self):
        pass

    def manage_account(self):
        pass

    def manage_database(self):
        pass


class Registered(User):
    def __init__(self, name, phone_number, email_address, password, available_time):
        super().__init__(None, available_time)
        self.name = name
        self.phone_number = phone_number
        self.email_address = email_address
        self.password = password
        self.favourite_recipe = None
        self.last_few_recipes = []

    def sign_in(email_address, password):
        user = RegisteredUser.objects.filter(email=email_address).first()
        if user and check_password(password, user.hashed_password):
            return f"Welcome back, {user.first_name}!"
        return "Invalid credentials"

    def save_recipe(self, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = RegisteredUser.objects.get(email=self.email_address)
        user.saved_recipes.add(recipe)
        return f"Recipe '{recipe.title}' saved successfully"

    def view_recipes(self):
        user = RegisteredUser.objects.get(email=self.email_address)
        last_recipes = user.last_used_recipes.all().order_by('-id')[:5]
        saved_recipes = user.saved_recipes.all()
        return {
            "last_viewed": [recipe.title for recipe in last_recipes],
            "saved_recipes": [recipe.title for recipe in saved_recipes]
        }
    
class Recipe:
    def __init__(self, ingredient_list, recipe_id, title):
        self.ingredient_list = ingredient_list
        self.recipe_id = recipe_id
        self.title = title

    def generate_recipe(self):
        pass


class LLM:
    def __init__(self, skill_level, available_time, ingredients, prompt, title):
        self.skill_level = skill_level
        self.available_time = available_time
        self.ingredients = ingredients
        self.prompt = prompt
        self.title = title

    def generate_recipe(self):
        pass

    def save_recipe(self):
        pass
