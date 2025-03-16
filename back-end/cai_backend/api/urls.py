from django.urls import path
from .views import generate_recipe

urlpatterns = [
    path("generate_recipe/", generate_recipe, name="generate_recipe")
]
