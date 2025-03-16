from django.urls import path
from .views import User

urlpatterns = [
    path("generate_recipe/", User.generate_recipe, name="generate_recipe")
]
